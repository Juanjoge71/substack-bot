import os
import re
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.constants import ParseMode

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
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

bot = Bot(token=BOT_TOKEN)

SUBSTACK_PATTERN = re.compile(r"https?://[^\s]+substack\.com[^\s]*", re.IGNORECASE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_endpoint = f"{WEBHOOK_URL}/webhook"
    await bot.set_webhook(url=webhook_endpoint)
    log.info(f"Webhook set: {webhook_endpoint}")
    yield
    await bot.delete_webhook()
    log.info("Webhook removed")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)

    if not update.message or not update.message.text:
        return {"ok": True}

    chat_id = update.message.chat_id
    text = update.message.text

    urls = SUBSTACK_PATTERN.findall(text)
    if not urls:
        return {"ok": True}

    url = urls[0]
    log.info(f"Processing Substack URL: {url}")

    await bot.send_message(chat_id=chat_id, text="⏳ Procesando artículo...")

    try:
        post = await fetch_substack_post(url)
        summary = await summarize_post(post, ANTHROPIC_API_KEY)
        capacities_url = await save_to_capacities(
            post, summary, CAPACITIES_API_KEY, CAPACITIES_SPACE_ID
        )

        reply = (
            f"✅ *{escape_md(post['title'])}*\n"
            f"_por {escape_md(post['author'])}_\n\n"
            f"{escape_md(summary)}\n\n"
            f"📎 [Ver en Capacities]({capacities_url})"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=reply,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True,
        )

    except Exception as e:
        log.error(f"Error processing {url}: {e}", exc_info=True)
        await bot.send_message(
            chat_id=chat_id,
            text=f"❌ Error procesando el artículo: {e}",
        )

    return {"ok": True}


def escape_md(text: str) -> str:
    """Escape Telegram MarkdownV2 special chars."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(special)}])", r"\\\1", text)


@app.get("/health")
async def health():
    return {"status": "ok"}
