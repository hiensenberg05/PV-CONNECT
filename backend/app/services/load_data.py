import os
import requests

# WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
# GRAPH_URL = "https://graph.facebook.com/v19.0"


# def download_media(media_id: str) -> dict:
#     """
#     Input:
#         media_id

#     Output:
#         {
#             file_path: str,
#             mime_type: str
#         }
#     """

#     headers = {
#         "Authorization": f"Bearer {WHATSAPP_TOKEN}"
#     }

#     # 1️⃣ Fetch metadata
#     meta_resp = requests.get(f"{GRAPH_URL}/{media_id}", headers=headers)
#     meta_resp.raise_for_status()
#     meta = meta_resp.json()

#     media_url = meta["url"]
#     mime_type = meta["mime_type"]

#     # 2️⃣ Download binary
#     bin_resp = requests.get(media_url, headers=headers)
#     bin_resp.raise_for_status()

#     ext = mime_type.split("/")[-1]
#     file_path = f"/tmp/{media_id}.{ext}"

#     with open(file_path, "wb") as f:
#         f.write(bin_resp.content)

#     return {
#         "file_path": file_path,
#         "mime_type": mime_type
#     }



def download_media(media_id: str) -> dict:
    """
    MOCK media loader for local testing
    """

    if "VOICE" in media_id:
        return {
            "file_path": "tests/sample_voice.wav",
            "mime_type": "audio/wav"
        }

    return {
        "file_path": "tests/sample_image.jpg",
        "mime_type": "image/jpeg"
    }
