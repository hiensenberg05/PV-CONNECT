# backend/app/services/load_data.py
"""
Media download service.
Downloads media from WhatsApp Graph API.
"""

import os
import requests
import mimetypes

# Read token from env (may be empty in tests)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
GRAPH_URL = "https://graph.facebook.com/v19.0"


def download_media(media_id: str) -> dict:
    """
    Download media from WhatsApp.

    Input:
        media_id: WhatsApp media ID

    Output:
        {
            file_path: str,
            mime_type: str
        }
    """
    # If media_id is a local path, return it directly (useful for tests)
    if media_id and os.path.exists(media_id):
        mime_type, _ = mimetypes.guess_type(media_id)
        return {
            "file_path": os.path.abspath(media_id),
            "mime_type": mime_type or "application/octet-stream"
        }

    # Check if we're in test/mock mode
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN == "test":
        # simple heuristic: if media_id looks like an audio file, return sample voice
        mid = (media_id or "").lower()
        if mid.endswith(('.wav', '.mp3', '.m4a')) or "voice" in mid:
            sample = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "sample_voice.wav")
            if os.path.exists(sample):
                return {"file_path": os.path.abspath(sample), "mime_type": "audio/wav"}
        # fallback to sample image
        sample_img = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "sample_image.jpg.jpeg")
        if os.path.exists(sample_img):
            return {"file_path": os.path.abspath(sample_img), "mime_type": "image/jpeg"}
        # Last resort: raise
        raise RuntimeError("No WHATSAPP_TOKEN and no local sample media available")

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}"
    }

    # 1. Fetch metadata
    meta_resp = requests.get(f"{GRAPH_URL}/{media_id}", headers=headers)
    meta_resp.raise_for_status()
    meta = meta_resp.json()

    media_url = meta["url"]
    mime_type = meta["mime_type"]

    # 2. Download binary
    bin_resp = requests.get(media_url, headers=headers)
    bin_resp.raise_for_status()

    ext = mime_type.split("/")[-1]
    file_path = f"/tmp/{media_id}.{ext}"

    with open(file_path, "wb") as f:
        f.write(bin_resp.content)

    return {
        "file_path": file_path,
        "mime_type": mime_type
    }


def _mock_download_(media_id: str) -> dict:
    """
    MOCK media loader for local testing.
    """
    if "VOICE" in media_id.upper():
        return {
            "file_path": "tests/sample_voice.wav",
            "mime_type": "audio/wav"
        }

    return {
        "file_path": "tests/sample_image.jpg",
        "mime_type": "image/jpeg"
    }
