from app.services.mongodb_service import find_user, find_doctor
from app.services.ollama_service import detect_user_type_from_message
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def detect_user_type_node(state: GraphState) -> GraphState:
    """
    Detect user type: patient or doctor
    Logic:
    1. Check database first
    2. If not found, analyze message content
    3. Default to patient (safer)
    """
    phone = state.get("from_number", "")
    message = state.get("message", "")
    
    # Step 1: Check verified doctor registry first (Trust Filter)
    doctor = await find_doctor(phone)
    if doctor:
        state["user_type"] = "doctor"
        state["is_verified"] = doctor.get("verified", False)
        state["doctor_name"] = doctor.get("name", "Doctor")
        logger.info(f"User {phone} identified as registered doctor: {doctor.get('name')}")
        return state
        
    # Step 2: Check existing user database
    user = await find_user(phone)
    if user and user.get("role") == "doctor":
        state["user_type"] = "doctor"
        state["is_verified"] = True
        logger.info(f"User {phone} identified as doctor from user DB")
        return state
    
    # Step 3: Analyze message content if not in DB
    if message:
        try:
            detected_type = await detect_user_type_from_message(message)
            if detected_type == "doctor":
                state["user_type"] = "doctor"
                state["is_verified"] = False  # Needs verification
                logger.info(f"User {phone} claims to be doctor (requires verification)")
            else:
                state["user_type"] = "patient"
                state["is_verified"] = False
        except Exception as e:
            logger.error(f"User type detection error: {e}")
            state["user_type"] = "patient"
    else:
        state["user_type"] = "patient"
    
    return state
