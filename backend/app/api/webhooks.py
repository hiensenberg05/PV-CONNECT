from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import requests
from app.agents.graph import graph

router = APIRouter()

# =========================================================
# CONFIG
# =========================================================
WHATSAPP_VERIFY_TOKEN = "my_verified_token_123"  # Must match Meta dashboard
WHATSAPP_API_VERSION = "v16.0"


# =========================================================
# WEBHOOK VERIFICATION (GET)
# =========================================================
@router.get("/")
async def verify_webhook(request: Request):
    """
    Meta webhook verification endpoint.
    Meta sends:
    hub.mode, hub.verify_token, hub.challenge
    """
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    raise HTTPException(status_code=403, detail="Webhook verification failed")


# =========================================================
# WEBHOOK RECEIVER (POST)
# =========================================================
@router.post("/")
async def whatsapp_webhook(request: Request):
    """
    Receives incoming WhatsApp messages & status events
    """
    payload = await request.json()
    print("📩 RAW WEBHOOK PAYLOAD:", payload)

    entry = payload.get("entry", [])
    if not entry:
        return {"status": "ignored"}

    changes = entry[0].get("changes", [])
    if not changes:
        return {"status": "ignored"}

    value = changes[0].get("value", {})

    # Ignore non-message events (like delivery/read receipts)
    if "messages" not in value:
        print("ℹ️ Non-message event received")
        return {"status": "ignored"}

    message = value["messages"][0]

    phone = message.get("from")
    text = (message.get("text") or {}).get("body", "")

    print(f"📞 From: {phone}")
    print(f"💬 Message: {text}")

    # Build AI state
    state = {
        "phone_number": phone,
        "current_message": text,
        "messages": [message],
        "documents": [],
        "voice_notes": [],
    }

    # Invoke your AI pipeline
    await graph.ainvoke(state)

    return {"status": "ok"}


# =========================================================
# SEND MESSAGE API
# =========================================================
@router.post("/send")
async def send_message_endpoint(payload: dict):
    """
    Send a WhatsApp message using Cloud API
    """
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_ID")

    if not token or not phone_id:
        raise HTTPException(status_code=500, detail="WhatsApp credentials not configured")

    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
