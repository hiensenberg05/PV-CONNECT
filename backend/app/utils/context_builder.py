# backend/app/utils/context_builder.py
"""
Context builder for LLM messages.
Handles Patient and Doctor flows with proper prompting and section-based progression.
"""

import os
from app.services.llm_service import get_model


def _load_text_file(path: str) -> str:
    """Load text file from the data directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, path)
    
    if not os.path.exists(full_path):
        return ""
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def _get_current_section_missing(state: dict) -> list:
    """
    Get missing fields (simplified - no section gating).
    Returns all missing fields.
    """
    return state.get("missing", [])


def _format_field_names_for_display(field_list: list) -> str:
    """
    Convert technical field names to human-readable questions.
    """
    field_map = {
        "patient_name": "Patient's name",
        "patient_gender": "Patient's gender",
        "patient_age_value": "Patient's age",
        "patient_age_unit": "Age unit (years/months/days)",
        "reason_for_medicine": "Reason for taking medicine",
        "medicine_advised_by": "Who advised the medicine",
        "self_medicated": "Whether self-medicated",
        "past_disease_history": "Past medical history",
        "medicine_name": "Medicine name",
        "medicine_quantity_taken": "Quantity taken",
        "medicine_dosage_form": "Dosage form (tablet/syrup/injection)",
        "medicine_expiry_date": "Medicine expiry date",
        "medicine_start_date": "When medicine was started",
        "medicine_stop_date": "When medicine was stopped",
        "side_effect_start_date": "When side effect started",
        "side_effect_continuing": "Is side effect continuing",
        "side_effect_stop_date": "When side effect stopped",
        "severity_no_daily_activity_effect": "Did it affect daily activities",
        "severity_affected_daily_activity": "How daily activities were affected",
        "severity_hospitalized": "Was patient hospitalized",
        "severity_death": "Did it result in death",
        "severity_other": "Other severity details",
        "side_effect_description": "Detailed description of side effect",
        "management_action_taken": "What action was taken"
    }
    
    return ", ".join([field_map.get(f, f) for f in field_list])


def _build_concise_chat_history(chat_history: list, max_turns: int = 3) -> str:
    """
    Build a concise summary of recent chat history.
    Only keep last N turns to prevent context pollution.
    """
    if not chat_history:
        return "No previous conversation."
    
    # Keep only last max_turns exchanges
    recent = chat_history[-max_turns*2:] if len(chat_history) > max_turns*2 else chat_history
    
    formatted = []
    for msg in recent:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "user":
            formatted.append(f"User said: {content}")
        elif role == "assistant":
            formatted.append(f"You asked: {content}")
    
    return "\n".join(formatted)


def build_llm_messages(state: dict) -> str:
    """
    Improved context builder with:
    - Section-based progression
    - Clear memory management
    - Reduced hallucination
    """

    user_type = state.get("user_type")
    curr_msg = state.get("current_message", "")
    to_use = state.get("to_use", "")
    all_missing = state.get("missing", [])
    already = state.get("extracted_data", {})
    prev_msgs = state.get("chat_history", [])
    problems = state.get("problems", [])
    has_given_doc = state.get("doc_id") is not None
    LANGUAGE = state.get("language", "en")

    # Case complete check
    if not all_missing:
        state["case_complete"] = True
        if user_type == "patient":
            return "धन्यवाद! सभी जानकारी मिल गई है। आपका केस सफलतापूर्वक सेव हो गया है।" if LANGUAGE == "hi" else "Thank you! All information received. Your case has been saved successfully."
        else:
            return "Thank you. All required clinical information has been collected. Case submitted successfully."

    # CRITICAL: Get only current section's missing fields
    target_missing = _get_current_section_missing(state)
    
    # Build concise history
    concise_history = _build_concise_chat_history(prev_msgs, max_turns=3)
    
    # Format fields for display
    readable_missing = _format_field_names_for_display(target_missing)

    client, model = get_model()

    if user_type == "patient":
        SYSTEM_PROMPT = _load_text_file("data/pv_patient.txt")
        
        # Fallback if file load fails
        if not SYSTEM_PROMPT:
            SYSTEM_PROMPT = (
                "You are a friendly Pharmacovigilance assistant.\n"
                "Collect: {readable_missing}\n"
                "Output NO_FOLLOWUP when done."
            )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(
                target_missing=target_missing,
                already_collected=list(already.keys()),
                readable_missing=readable_missing,
                problems=problems
            )},
            {"role": "system", "content": f"User's current message: {curr_msg}"},
            {"role": "system", "content": f"Information already collected (DO NOT ask again):\n{already}"},
            {"role": "system", "content": f"Recent conversation:\n{concise_history}"},
        ]
        
        if problems:
            messages.append({"role": "system", "content": f"Issues with current input: {', '.join(problems)}"})
        
        if has_given_doc:
            messages.append({"role": "system", "content": "User has already provided a document/prescription."})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,  # Lower temperature for more consistent responses
            max_tokens=150   # Limit response length
        )

        output = response.choices[0].message.content.strip()
        return output

    elif user_type == "doctor":
        DOCTOR_SYSTEM_PROMPT = _load_text_file("data/pv_doctor.txt")
        
        if not DOCTOR_SYSTEM_PROMPT:
            DOCTOR_SYSTEM_PROMPT = (
                "You are a professional PV assistant.\n"
                "Collect: {readable_missing}\n"
                "Output NO_FOLLOWUP when done."
            )

        messages = [
            {"role": "system", "content": DOCTOR_SYSTEM_PROMPT.format(
                target_missing=target_missing,
                already_collected=list(already.keys()),
                readable_missing=readable_missing
            )},
            {"role": "system", "content": f"Provider's message: {curr_msg}"},
            {"role": "system", "content": f"Data collected:\n{already}"},
            {"role": "system", "content": f"Recent exchange:\n{concise_history}"},
        ]
        
        if problems:
            messages.append({"role": "system", "content": f"Technical issues: {', '.join(problems)}"})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=150
        )

        output = response.choices[0].message.content.strip()
        return output

    else:
        return "Please tell me if you are a Patient or a Doctor."