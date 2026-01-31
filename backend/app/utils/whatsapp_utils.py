# backend/app/utils/whatsapp_utils.py
"""
WhatsApp utility functions for the PV-CONNECT backend.
Handles sending messages and parsing incoming webhook payloads.
"""

import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"


def get_text_message_input(recipient: str, text: str) -> dict:
    """Format a text message payload for WhatsApp API."""
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }


async def send_whatsapp_message(recipient: str, text: str) -> bool:
    """
    Send a text message to a WhatsApp user.
    
    Args:
        recipient: The WhatsApp ID (phone number) of the recipient.
        text: The message text to send.
        
    Returns:
        True if successful, False otherwise.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
    }
    payload = get_text_message_input(recipient, text)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                WHATSAPP_API_URL, json=payload, headers=headers, timeout=10.0
            )
            response.raise_for_status()
            logger.info(f"Message sent to {recipient}: {response.status_code}")
            return True
    except httpx.TimeoutException:
        logger.error(f"Timeout sending message to {recipient}")
        return False
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error sending message: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False


def is_valid_whatsapp_message(body: dict) -> bool:
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )


def extract_message_data(body: dict) -> dict | None:
    """
    Extract relevant data from a WhatsApp webhook payload.
    
    Returns:
        A dict with phone_number, name, message_type, and content, or None if invalid.
    """
    if not is_valid_whatsapp_message(body):
        return None

    value = body["entry"][0]["changes"][0]["value"]
    contact = value["contacts"][0]
    message = value["messages"][0]

    phone_number = contact["wa_id"]
    # Normalize phone number to include + prefix
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    name = contact.get("profile", {}).get("name", "Unknown")
    message_type = message.get("type", "text")

    content = None
    media_id = None

    if message_type == "text":
        content = message.get("text", {}).get("body")
    elif message_type == "image":
        media_id = message.get("image", {}).get("id")
    elif message_type == "audio":
        media_id = message.get("audio", {}).get("id")
    elif message_type == "document":
        media_id = message.get("document", {}).get("id")

    return {
        "phone_number": phone_number,
        "name": name,
        "message_type": message_type,
        "text_content": content,
        "media_id": media_id,
    }
