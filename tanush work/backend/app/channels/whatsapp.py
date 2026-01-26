import httpx
from app.config import WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
import logging

logger = logging.getLogger(__name__)

API_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


async def send_whatsapp_message(phone: str, text: str) -> bool:
    """Send WhatsApp message. Returns True if successful."""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        logger.warning("WhatsApp credentials not configured")
        return False
    
    if not phone or not text:
        logger.warning(f"Invalid message params: phone={phone}, text={bool(text)}")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": text}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Message sent to {phone}")
            return True
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False
