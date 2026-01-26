from datetime import datetime
from app.services.mongodb_service import upsert_case, save_message
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


def generate_case_id(phone: str) -> str:
    """Generate case ID (placeholder - TODO: Replace with proper ID generation)"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    # TODO: Add sequence number or UUID
    return f"CASE_{timestamp}_{phone[-4:]}"


async def save_case_node(state: GraphState) -> GraphState:
    """
    Persist case to MongoDB
    Saves to cases collection and messages collection
    """
    from_number = state.get("from_number", "")
    case_id = state.get("case_id")
    
    # Generate case_id if not exists
    if not case_id:
        case_id = generate_case_id(from_number)
        state["case_id"] = case_id
    
    # Prepare case data
    case_data = {
        "case_id": case_id,
        "phone_number": from_number,
        "language": state.get("language", "en"),
        "user_type": state.get("user_type", "patient"),
        "extracted_data": state.get("extracted_data", {}),
        "documents": state.get("documents", []),
        "voice_notes": state.get("voice_notes", []),
        "risk_level": state.get("risk_level", "medium"),
        "triage_reason": state.get("triage_reason", ""),
        "is_complete": state.get("is_complete", False),
        "completeness_score": state.get("completeness_score", 0.0),
        "confidence_score": state.get("confidence_score", 0.0),
        "requires_human_review": state.get("requires_human_review", False),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "status": "open"
    }
    
    try:
        # Save case
        result = await upsert_case(case_data)
        
        # Save message to conversation history
        message = state.get("message", "")
        if message:
            await save_message(from_number, message, role="user", case_id=case_id)
        
        logger.info(f"Case saved: {case_id}")
        
    except Exception as e:
        logger.error(f"Error saving case: {e}")
        # Don't fail the workflow - case_id is still set
    
    return state
