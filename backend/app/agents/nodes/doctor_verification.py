from app.services.mongodb_service import find_user
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def verify_doctor_node(state: GraphState) -> GraphState:
    """
    Verify doctor credentials
    - Check if doctor exists in database and is verified
    - If not verified, request license upload (non-blocking)
    - Doctor verification runs in background (human-in-the-loop)
    """
    phone = state.get("from_number", "")
    
    if not phone:
        logger.warning("No phone number in doctor verification")
        state["user_type"] = "patient"  # Fallback to patient
        return state
    
    # Check database for verified doctor
    user = await find_user(phone)
    
    if user and user.get("role") == "doctor" and user.get("verified"):
        logger.info(f"Doctor {phone} is verified")
        # Doctor is verified - allow to proceed
        # TODO: Implement doctor case update path
        state["user_type"] = "doctor"
        return state
    
    # Doctor not verified - request license
    # This is non-blocking - verification happens in background
    logger.info(f"Doctor {phone} not verified - requesting license")
    state["next_question"] = "Please upload your medical license for verification. We'll review it and notify you once verified."
    # TODO: Mark for background human review
    # TODO: Implement license upload handling
    
    return state
