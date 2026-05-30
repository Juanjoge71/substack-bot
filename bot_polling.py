import os
import re
import logging
import asyncio
import httpx

from dotenv import load_dotenv
from substack import fetch_substack_post
from summarizer import summarize_post
from capacities import save_to_capacities

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CAPACITIES_API_KEY = os.environ["CAPACITIES_API_KEY"]
CAPACITIES_SPACE_ID = os.environ["CAPACITIES_SPACE_ID"]

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
SUBSTACK_PATTERN = re.compile(r"https?://[^\s]*substack\.com[^\s]*", re.IGNORECASE)


async def send_message(client: httpx.AsyncClient, chat_id: int, text: str):
    await client.post(f"{TG_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    })


async def process_update(client: httpx.AsyncClient, update: dict):
    message = update.get("message") or update.get("channel_post")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    log.info(f"Mensaje de chat {chat_id}: {text[:80]}")

    urls = SUBSTACK_PATTERN.findall(text)
    if not urls:
        return

    url = urls[0]
    log.info(f"Procesando: {url}")

    await send_message(client, chat_id, "⏳ Procesando artículo...")

    try:
        post = await fetch_substack_post(url)
        summary = await summarize_post(post, ANTHROPIC_API_KEY)
        capacities_url = await save_to_capacities(
            post, summary, CAPACITIES_API_KEY, CAPACITIES_SPACE_ID
        )

        header = f"✅ {post['title']}\nPor: {post['author']}\n\n"
        footer = f"\n\n📎 Ver en Capacities: {capacities_url}"
        full = header + summary + footer

        # Split into chunks of max 4000 chars at newline boundaries
        chunks = []
        current = ""
        for line in full.splitlines(keepends=True):
            if len(current) + len(line) > 4000:
                chunks.append(current)
                current = line
            else:
                current += line
        if current:
            chunks.append(current)

        for chunk in chunks:
            await send_message(client, chat_id, chunk)

        log.info(f"Respuesta enviada OK ({len(chunks)} mensaje(s))")

    except Exception as e:
        log.error(f"Error: {e}", exc_info=True)
        await send_message(client, chat_id, f"❌ Error: {e}")


async def main():
    # Delete any existing webhook so polling works
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{TG_API}/deleteWebhook", json={"drop_pending_updates": False})
        log.info(f"deleteWebhook: {r.json()}")

    offset = 0
    log.info("Bot iniciado — esperando mensajes (Ctrl+C para detener)")

    async with httpx.AsyncClient(timeout=35) as client:
        while True:
            try:
                r = await client.post(f"{TG_API}/getUpdates", json={
                    "offset": offset,
                    "timeout": 30,
                    "allowed_updates": ["message", "channel_post"],
                })
                data = r.json()

                if not data.get("ok"):
                    log.error(f"getUpdates error: {data}")
                    await asyncio.sleep(5)
                    continue

                updates = data.get("result", [])
                if updates:
                    log.info(f"{len(updates)} update(s) recibido(s)")

                for update in updates:
                    offset = update["update_id"] + 1
                    await process_update(client, update)

            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Polling error: {e}")
                await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
