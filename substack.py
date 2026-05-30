import httpx
from bs4 import BeautifulSoup
import re


async def fetch_substack_post(url: str) -> dict:
    """Fetch and parse a Substack post. Returns title, author, content."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    title = _extract_title(soup)
    author = _extract_author(soup)
    content = _extract_content(soup)

    return {"url": url, "title": title, "author": author, "content": content}


def _extract_title(soup: BeautifulSoup) -> str:
    for sel in ["h1.post-title", "h1[class*='title']", "h1"]:
        tag = soup.select_one(sel)
        if tag:
            return tag.get_text(strip=True)
    meta = soup.find("meta", property="og:title")
    return meta["content"] if meta else "Sin título"


def _extract_author(soup: BeautifulSoup) -> str:
    for sel in [
        "a.author-name",
        "[class*='author'] a",
        "span[class*='author']",
    ]:
        tag = soup.select_one(sel)
        if tag:
            return tag.get_text(strip=True)
    meta = soup.find("meta", attrs={"name": "author"})
    return meta["content"] if meta else "Autor desconocido"


def _extract_content(soup: BeautifulSoup) -> str:
    # Substack post body
    body = soup.select_one("div.available-content") or soup.select_one(
        "div[class*='post-content']"
    )
    if not body:
        body = soup.select_one("article")
    if not body:
        return ""

    # Remove script/style/paywall noise
    for tag in body.select("script, style, .paywall, .subscribe-widget"):
        tag.decompose()

    text = body.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:12000]  # cap at ~12k chars for Claude context
