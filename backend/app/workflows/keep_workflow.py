# backend/app/workflows/keep_workflow.py
"""
Main workflow orchestrator - FIXED VERSION
Uses cache for fast state, DB verification for doctors, async license check.

FIXES:
1. Removed unused imports
2. Removed redundant problems reset
3. Added doctor verification edge case handling
4. Better error handling

Flow:
1. Receive message from WhatsApp
2. Get state from cache (fast)
3. If no state -> Ask user type -> Initialize state
4. If doctor -> Verify by phone OR submit license for async check
5. Route to pv_followup_agent
6. Save state to cache
7. If case_complete -> Save to MongoDB
8. Return reply
"""

from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

from .cache_store import get_state, set_state, delete_state
from .router import extract_user_type, get_user_type_question
from .verify_doctorno import verify_doctor_by_phone, add_doctor_pending_verification
from .asynchronous_licensecheck import check_verification_status
from .state_save import save_state

from app.agents.pv_followup_agent import run_pv_followup_agent
from app.schemas.conversation_state import ConversationState


def create_initial_state(phone_number: str, user_type: str) -> Dict[str, Any]:
    """
    Create a fresh state for a new conversation using schema.
    """
    state = ConversationState(
        case_id=str(uuid4()),
        phone_number=phone_number,
        user_type=user_type,
        workflow_stage="COLLECTING",
        verified_doctor=False if user_type == "doctor" else None,
        human_verified=False if user_type == "doctor" else None,
    )
    return state.to_dict()


def reset_per_turn_keys(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reset keys that should be cleared every new message.
    """
    state["current_message"] = None
    state["doc_id"] = None
    state["voice_id"] = None
    state["current_doc_data"] = {}
    state["current_voice_data"] = {}
    state["to_use"] = ""
    # Initialize problems if not exists (will be populated by agent)
    if "problems" not in state:
        state["problems"] = []
    return state


async def process_message(
    phone_number: str,
    text_content: Optional[str] = None,
    doc_id: Optional[str] = None,
    voice_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point. Process an incoming message and return a reply.
    """

    # Step 1: Get state from cache (fast)
    state = get_state(phone_number)

    # Step 2: No state -> Ask user type or create new state
    if state is None:
        user_type = extract_user_type(text_content or "")

        if user_type is None:
            # First contact or unclear - ask user type
            return {
                "reply": get_user_type_question(),
                "state": None
            }
        else:
            # User replied with type - create state
            state = create_initial_state(phone_number, user_type)
            set_state(phone_number, state)  # SAVE STATE

    # Step 3: Doctor verification flow
    if state.get("user_type") == "doctor":

        # Check if already verified
        if state.get("verified_doctor") is not True:

            # First, check DB for doctor by phone number
            verification = await verify_doctor_by_phone(phone_number)

            if verification["is_verified"]:
                # Pre-verified doctor in DB
                state["verified_doctor"] = True
                state["human_verified"] = True
                # Store doctor info from DB
                if verification["doctor_data"]:
                    state["doctor_name"] = verification["doctor_data"].get("name")
                    state["doctor_id"] = verification["doctor_data"].get("doctor_id")

            elif verification["exists"] and not verification["is_verified"]:
                # Doctor in DB but not yet verified - allow chat, pending human review
                state["verified_doctor"] = True
                state["human_verified"] = False
                if verification["doctor_data"]:
                    state["doctor_name"] = verification["doctor_data"].get("name")
                    state["doctor_id"] = verification["doctor_data"].get("doctor_id")

            elif doc_id and not state.get("license_id"):
                # New doctor sent license image - add to DB as pending
                state["license_id"] = doc_id
                try:
                    doctor_id = await add_doctor_pending_verification(
                        phone_number=phone_number,
                        license_id=doc_id
                    )
                    state["doctor_id"] = doctor_id
                    state["verified_doctor"] = True  # Allow chat to continue
                    state["human_verified"] = False  # Pending human review
                except Exception as e:
                    # If doctor registration fails, ask to try again
                    set_state(phone_number, state)  # SAVE STATE
                    return {
                        "reply": "Error registering license. Please try uploading again.",
                        "state": state
                    }

            elif state.get("verification_id"):
                # Check if async verification completed
                status = await check_verification_status(phone_number)
                if status["verified"]:
                    state["human_verified"] = True
                    state["verified_doctor"] = True
            
            else:
                # FIX: No verification path matched - ask for license
                # This handles: not in DB, no doc_id sent, no verification_id
                set_state(phone_number, state)  # SAVE STATE
                return {
                    "reply": "Please upload your medical license ID to verify your identity.",
                    "state": state
                }

    # Step 4: Update per-turn data
    state = reset_per_turn_keys(state)
    state["current_message"] = text_content or ""
    state["doc_id"] = doc_id
    state["voice_id"] = voice_id

    # Step 5: Run the agent
    try:
        state = run_pv_followup_agent(state)
    except Exception as e:
        import traceback
        print(f"[keep_workflow] Agent error: {str(e)}")
        traceback.print_exc()
        # Return a safe fallback
        return {
            "reply": "Sorry, there was an error processing your message. Please try again.",
            "state": state
        }

    # Step 6: Save state to cache
    set_state(phone_number, state)

    # Step 7: If case complete, save to MongoDB
    if state.get("case_complete") is True:
        try:
            await save_state(state)  # Persist to DB
            delete_state(phone_number)  # Clear cache
        except Exception as e:
            print(f"[keep_workflow] Error saving state: {str(e)}")
            # Don't clear cache if save failed - allows retry

    # Step 8: Return reply
    return {
        "reply": state.get("followup_msg", "Thank you for your message."),
        "state": state
    }