# app/services/whatsapp_media_service.py

import httpx
from app.config import WHATSAPP_ACCESS_TOKEN

GRAPH_API_BASE = "https://graph.facebook.com/v18.0"


async def download_whatsapp_media(media_id: str) -> bytes:
    """
    Given a WhatsApp media_id, downloads and returns raw media bytes.
    """
    if not WHATSAPP_ACCESS_TOKEN or not media_id:
        return b""

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        # 1️⃣ Get media URL
        meta_resp = await client.get(
            f"{GRAPH_API_BASE}/{media_id}",
            headers=headers,
        )
        meta_resp.raise_for_status()
        media_url = meta_resp.json().get("url")

        if not media_url:
            return b""

        # 2️⃣ Download actual media bytes
        media_resp = await client.get(
            media_url,
            headers=headers,
        )
        media_resp.raise_for_status()

        return media_resp.content
