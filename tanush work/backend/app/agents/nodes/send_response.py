from app.channels.whatsapp import send_whatsapp_message
from app.services.mongodb_service import save_message
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def send_response_node(state: GraphState) -> GraphState:
    """
    Send response via WhatsApp (if configured) or return response in state
    Handles both complete case confirmation and follow-up questions
    Works without WhatsApp - response is stored in state for testing
    """
    from_number = state.get("from_number", "")
    case_id = state.get("case_id", "")
    is_complete = state.get("is_complete", False)
    next_question = state.get("next_question")
    
    # Determine message content
    if is_complete:
        message = f"Thank you! Your report (ID: {case_id}) has been recorded. We will review it shortly."
    elif next_question:
        message = next_question
    else:
        message = "Thank you for your report. We'll get back to you soon."
    
    # Store response in state (for testing/API access)
    state["response_message"] = message
    
    # Try to send via WhatsApp (if configured)
    # Disabled per user request
    if from_number and False:  # Forced disabled
        try:
            success = await send_whatsapp_message(from_number, message)
            if success:
                # Save assistant message to conversation history
                await save_message(from_number, message, role="assistant", case_id=case_id)
                logger.info(f"Response sent to {from_number}")
            else:
                logger.warning(f"Failed to send WhatsApp message (may not be configured)")
                # Still save to history for testing
                await save_message(from_number, message, role="assistant", case_id=case_id)
            state["response_sent"] = success
        except Exception as e:
            logger.warning(f"WhatsApp send failed (continuing): {e}")
            state["response_sent"] = False
    else:
        # No phone number or disabled - just log the response (for testing)
        if from_number:
             # Even if disabled, we probably want to save the assistant message to DB so history works?
             # The original code saved it inside the try/else blocks.
             # Let's verify if we should save it here.
             await save_message(from_number, message, role="assistant", case_id=case_id)
        
        logger.info(f"Response generated (WhatsApp disabled): {message}")
        state["response_sent"] = True  # Mark as "sent" for testing purposes

    
    return state
