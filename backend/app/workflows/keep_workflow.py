# backend/app/workflows/keep_workflow.py
"""
Main workflow orchestrator with chat continuation support.
Uses cache for fast state, DB verification for doctors, async license check.

Flow:
1. Receive message from WhatsApp
2. Check for exit command
3. Get state from cache (fast)
4. If no state -> Ask for Case ID or new case
5. If Case ID provided -> Load from DB
6. If doctor -> Verify by phone OR submit license for async check
7. Route to pv_followup_agent
8. Save state to cache and DB
9. Return reply
"""

from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
import re

from .cache_store import get_state, set_state, delete_state
from .router import extract_user_type, get_user_type_question, get_case_id_question, is_new_case_request, is_exit_request
from .verify_doctorno import verify_doctor_by_phone, add_doctor_pending_verification
from .asynchronous_licensecheck import check_verification_status
from .state_save import save_state, get_state_by_case_id

from app.agents.pv_followup_agent import run_pv_followup_agent, _detect_language
from app.schemas.conversation_state import ConversationState
from app.services.convert_lang_msg import convert_to_language


def generate_short_case_id() -> str:
    """
    Generate an 8-character Base36 case ID from UUID.
    Example output: "k5m2x9ab"
    Uses top 40 bits of UUID for ~1 trillion unique values.
    """
    num = uuid4().int >> 88  # Use top 40 bits for more entropy
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""
    while num:
        result = chars[num % 36] + result
        num //= 36
    return result.zfill(8)[:8]  # Ensure exactly 8 characters


# Matches both old UUID format (36 chars) and new 8-char Base36 format
CASE_ID_PATTERN = r'^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-z]{8})$'


def create_initial_state(phone_number: str, user_type: str) -> Dict[str, Any]:
    """
    Create a fresh state for a new conversation using schema.
    """
    state = ConversationState(
        case_id=generate_short_case_id(),
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
    if state:
        print(f"[DEBUG] State found. Type={state.get('user_type')} Verified={state.get('verified_doctor')}")
        # Update last activity timestamp
        state["last_activity"] = datetime.now().isoformat()
        set_state(phone_number, state)
    else:
        print("[DEBUG] No state found in cache")

    # Step 1b: Check for exit command
    if state and is_exit_request(text_content or ""):
        case_id = state.get("case_id", "N/A")
        lang = state.get("language", "en")
        print(f"[EXIT] User requested exit for Case {case_id}. Performing FINAL SAVE.")
        # Save state before exit
        print(f"[Exit] User exited. Saving case {case_id} to DB...")
        await save_state(state)
        # Clear cache
        delete_state(phone_number)
        
        exit_msg = (
            f"✅ *Session Ended Successfully*\n\n"
            f"Your Case ID is:\n*{case_id}*\n\n"
            f"📋 To continue later, simply paste this Case ID when you return.\n\n"
            f"If you are unable to provide further information, please share this Case ID with your prescribing physician.\n\n"
            f"Thank you for using PV-CONNECT! 🏥"
        )
        
        return {
            "reply": convert_to_language(exit_msg, lang),
            "state": None
        }

    # Step 2: No state -> Ask for Case ID first (new flow)
    if state is None:
        msg = (text_content or "").strip().lower()
        
        # Detect language from user's first message
        detected_lang = _detect_language(text_content or "")

        # Check if user sent a Case ID (UUID format)
        if re.match(CASE_ID_PATTERN, msg):
            # Try to find case in DB
            existing_state = await get_state_by_case_id(msg)
            if existing_state:
                # Found case - ask Patient/Doctor before loading
                print(f"[Resume] Case {msg} found. Asking user type first.")
                # Create temporary state with pending case ID
                state = {
                    "phone_number": phone_number,
                    "pending_case_id": msg,
                    "workflow_stage": "ASK_USER_TYPE",
                    "language": existing_state.get("language", detected_lang)
                }
                set_state(phone_number, state)
                
                lang = state["language"]
                case_found_msg = "✅ *Case Found*\n\nWe have located your case in our system.\n\n*Please identify yourself:*\n\n👤 Reply *1* for *Patient*\n👨‍⚕️ Reply *2* for *Healthcare Professional*"
                
                return {
                    "reply": convert_to_language(case_found_msg, lang),
                    "state": state
                }
            else:
                # Case ID not found - ask Patient/Doctor for new case
                case_not_found_msg = "⚠️ *Case Not Found*\n\nThe provided Case ID was not found in our records.\n\n*Please identify yourself to start a new case:*\n\n👤 Reply *1* for *Patient*\n👨‍⚕️ Reply *2* for *Healthcare Professional*"
                return {
                    "reply": convert_to_language(case_not_found_msg, detected_lang),
                    "state": None
                }

        # Check if user wants new case
        elif is_new_case_request(msg):
            # Start new case - ask Patient/Doctor
            return {
                "reply": convert_to_language(get_user_type_question(), detected_lang),
                "state": None
            }

        # Check if user indicated patient/doctor
        user_type = extract_user_type(msg)
        if user_type:
            # User replied with type - create state
            state = create_initial_state(phone_number, user_type)
            set_state(phone_number, state)
        else:
            # First contact - ask for Case ID
            return {
                "reply": convert_to_language(get_case_id_question(), detected_lang),
                "state": None
            }

    # Step 2b: Check if we have a pending case to load after user type selection
    if state and state.get("pending_case_id") and state.get("user_type") is None:
        user_type = extract_user_type(text_content or "")
        if user_type:
            pending_case_id = state["pending_case_id"]
            # Load the case from DB
            existing_state = await get_state_by_case_id(pending_case_id)
            if existing_state:
                print(f"[Resume] Loading case {pending_case_id} as {user_type}")
                existing_state.pop("_id", None)
                existing_state["phone_number"] = phone_number
                existing_state["user_type"] = user_type
                if user_type == "doctor":
                    existing_state["verified_doctor"] = False  # Doctor needs verification
                set_state(phone_number, existing_state)
                
                lang = existing_state.get("language", "en")
                loaded_msg = f"✅ *Case Loaded Successfully*\n\nCase ID: *{pending_case_id}*\nRole: *{user_type.upper()}*\n\nResuming from where you left off. Please proceed with the next question."
                
                return {
                    "reply": convert_to_language(loaded_msg, lang),
                    "state": existing_state
                }
        # Still waiting for valid user type
        return {
            "reply": "*Please identify yourself:*\n\n👤 Reply *1* for *Patient*\n👨‍⚕️ Reply *2* for *Healthcare Professional*",
            "state": state
        }

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
                    set_state(phone_number, state)
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
                # No verification path matched - ask for license
                set_state(phone_number, state)
                return {
                    "reply": "Please upload your medical license ID to verify your identity.",
                    "state": state
                }

        # CASE ID HANDOFF CHECK: After verification, check if verified doctor sent a Case ID
        if state.get("verified_doctor") is True and text_content:
            if re.match(CASE_ID_PATTERN, text_content.strip().lower()):
                target_case_id = text_content.strip().lower()
                print(f"[Handoff] Doctor {phone_number} requesting case {target_case_id}")

                # Fetch patient state from DB
                patient_state_dict = await get_state_by_case_id(target_case_id)

                if patient_state_dict:
                    print(f"[Handoff] Found case data for {target_case_id}")

                    # Copy relevant fields from patient state
                    fields_to_copy = [
                        "case_id",
                        "extracted_data",
                        "missing",
                        "chat_history",
                        "doc_all",
                        "voice_all",
                        "problems",
                        "current_section_index"
                    ]

                    for field in fields_to_copy:
                        if field in patient_state_dict:
                            state[field] = patient_state_dict[field]

                    # Add system note to history
                    if "chat_history" not in state:
                        state["chat_history"] = []
                    state["chat_history"].append({
                        "role": "system",
                        "content": f"Doctor {state.get('doctor_name', 'Unknown')} took over the case."
                    })

                    state["followup_msg"] = (
                        f"Case {target_case_id} loaded successfully.\n"
                        f"Patient data retrieved. Resuming data collection."
                    )

                    # Save immediately merged state
                    set_state(phone_number, state)
                    await save_state(state)

                    return {
                        "reply": state["followup_msg"],
                        "state": state
                    }
                else:
                    return {
                        "reply": f"Case ID {target_case_id} not found in database.",
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
        
        # SAFETY NET: Try to save whatever state we have before returning error
        try:
            print("[keep_workflow] Attempting emergency save during error...")
            await save_state(state)
        except Exception as save_err:
            print(f"[keep_workflow] Emergency save failed: {str(save_err)}")

        # Return a safe fallback
        return {
            "reply": "Sorry, there was an error processing your message. Please try again.",
            "state": state
        }

    # Step 6: Save state to cache
    set_state(phone_number, state)

    # Step 7: ALWAYS save state to MongoDB (Partial & Complete)
    try:
        await save_state(state)  # Persist to DB on every turn
    except Exception as e:
        print(f"[keep_workflow] Error saving state: {str(e)}")

    # Step 8: If case complete, clear cache
    if state.get("case_complete") is True:
        delete_state(phone_number)  # Clear cache only on completion

    # Step 9: Return reply
    return {
        "reply": state.get("followup_msg", "Thank you for your message."),
        "state": state
    }