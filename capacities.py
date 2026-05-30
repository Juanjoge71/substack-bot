import httpx

CAPACITIES_BASE = "https://api.capacities.io"


async def save_to_capacities(
    post: dict,
    summary: str,
    api_key: str,
    space_id: str,
) -> str:
    """
    Creates a Weblink object in Capacities with the summary as notes.
    Returns the URL of the created object.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "spaceId": space_id,
        "url": post["url"],
        "titleOverwrite": post["title"],
        "mdText": f"**Autor:** {post['author']}\n\n{summary}",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            f"{CAPACITIES_BASE}/save-weblink",
            json=payload,
            headers=headers,
        )
        if resp.status_code >= 400:
            import logging
            logging.getLogger(__name__).error(f"Capacities error {resp.status_code}: {resp.text}")
        resp.raise_for_status()
        data = resp.json()

    return data.get("url", post["url"])
