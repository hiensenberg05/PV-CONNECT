# backend/app/api/webhooks.py
"""
WhatsApp Webhook Endpoints for PV-CONNECT.
Handles incoming WhatsApp messages and verification.
"""

from fastapi import APIRouter, Request, HTTPException, Query
from app.config import settings
from app.workflows.keep_workflow import process_message
from app.utils.whatsapp_utils import (
    is_valid_whatsapp_message,
    extract_message_data,
    send_whatsapp_message,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    WhatsApp webhook verification endpoint.
    Meta sends a GET request to verify the webhook URL.
    """
    if hub_mode and hub_verify_token:
        if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("WEBHOOK_VERIFIED")
            return int(hub_challenge)
        else:
            logger.warning("VERIFICATION_FAILED")
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        logger.warning("MISSING_PARAMETER")
        raise HTTPException(status_code=400, detail="Missing parameters")


@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle incoming WhatsApp messages.
    Processes the message through the workflow and sends back a reply.
    """
    try:
        body = await request.json()
    except Exception:
        logger.error("Failed to parse JSON body")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Check if it's a status update (sent, delivered, read) - ignore these
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logger.info("Received WhatsApp status update, ignoring.")
        return {"status": "ok"}

    # Validate and extract message data
    if not is_valid_whatsapp_message(body):
        logger.warning("Not a valid WhatsApp message event")
        return {"status": "ok"}  # Return 200 to prevent Meta retries

    message_data = extract_message_data(body)
    if not message_data:
        logger.warning("Could not extract message data")
        return {"status": "ok"}

    phone_number = message_data["phone_number"]
    name = message_data["name"]
    message_type = message_data["message_type"]
    text_content = message_data["text_content"]
    media_id = message_data["media_id"]

    # Log the received message
    logger.info(f"Message received from {name} ({phone_number}): {text_content or f'[{message_type}]'}")

    # Process through workflow
    try:
        doc_id = media_id if message_type in ["image", "document"] else None
        voice_id = media_id if message_type == "audio" else None

        result = await process_message(
            phone_number=phone_number,
            text_content=text_content,
            doc_id=doc_id,
            voice_id=voice_id,
        )

        reply_text = result.get("reply", "Sorry, I couldn't process that.")

        # Send the reply back to WhatsApp
        await send_whatsapp_message(phone_number, reply_text)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await send_whatsapp_message(
            phone_number, "Sorry, a technical error occurred. Please try again later."
        )

    return {"status": "ok"}
