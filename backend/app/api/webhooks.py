from fastapi import APIRouter, HTTPException
from app.schemas.message import MessageIn, MessageOut
from app.workflows.keep_workflow import process_message
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/webhook", response_model=MessageOut)
async def whatsapp_webhook(message: MessageIn):
    """
    Unified webhook entry point using the new keep_workflow engine.
    Adapts MessageIn schema to process_message arguments.
    """
    try:
        logger.info(f"Webhook received from {message.phone_number} type={message.message_type}")
        
        # 1. Map Schema to Workflow Arguments
        text_content = message.text_content
        doc_id = None
        voice_id = None
        
        if message.message_type == "image":
            doc_id = message.image_media_id
        elif message.message_type == "document":
            doc_id = message.document_media_id
        elif message.message_type == "audio":
            voice_id = message.audio_media_id
            
        # 2. Process via Workflow Engine
        result = await process_message(
            phone_number=message.phone_number,
            text_content=text_content,
            doc_id=doc_id,
            voice_id=voice_id
        )
        
        # 3. Format Response
        reply_text = result.get("reply", "Sorry, I couldn't process that.")
        state = result.get("state", {})
        
        return MessageOut(
            text=reply_text,
            language=state.get("language", "en"),
            requires_input=True,
            metadata={"state_id": state.get("case_id")}
        )
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        # Return safe fallback to prevent retries loop from WhatsApp
        return MessageOut(
            text="Sorry, a technical error occurred. Please try again later.",
            requires_input=False
        )
