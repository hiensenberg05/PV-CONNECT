# backend/app/utils/context_builder.py
"""
Context builder for LLM messages.
Handles Patient and Doctor flows with proper prompting and section-based progression.

FIXES (Structure Preserved):
1. Added _advance_section_if_needed() for automatic progression
2. Better field ordering using sections
3. Stricter already_collected filtering
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


def _advance_section_if_needed(state: dict) -> dict:
    """
    NEW FUNCTION: Check if current section is complete and advance.
    This prevents LLM from asking about completed sections.
    """
    from app.schemas.conversation_state import SECTIONS_ORDER
    
    current_idx = state.get("current_section_index", 0)
    all_missing = state.get("missing", [])
    
    # Check if current section is complete
    if current_idx < len(SECTIONS_ORDER):
        current_section_fields = SECTIONS_ORDER[current_idx]
        section_complete = all(f not in all_missing for f in current_section_fields)
        
        if section_complete:
            # Move to next section
            state["current_section_index"] = current_idx + 1
            print(f"[Section] ✓ Section {current_idx + 1} complete → Moving to section {current_idx + 2}")
    
    return state


def _is_case_sufficient(state: dict) -> bool:
    """
    Check if we have sufficient data to complete the case even if some optional fields missing.
    
    Required for completion:
    - Patient info (name, gender, age)
    - Medicine (name)
    - Side effect (description)
    
    Optional (can auto-fill):
    - Severity fields (default to "no")
    - Past history (default to "None")
    
    Returns:
        True if case has minimum required data
    """
    extracted = state.get("extracted_data", {})
    
    # Core required fields
    required_fields = [
        "patient_name",
        "patient_gender", 
        "patient_age_value",
        "medicine_name",
        "side_effect_description"
    ]
    
    # Check if all required present and non-null
    has_required = all(
        extracted.get(field) not in [None, "", "None"] 
        for field in required_fields
    )
    
    return has_required


def _auto_fill_optional_fields(state: dict) -> dict:
    """
    Auto-fill remaining optional fields with sensible defaults.
    Called when case is sufficient but some fields still missing.
    
    Rules:
    - severity_* fields → "no" (no severe outcomes if not mentioned)
    - past_disease_history → "None" (no history if not mentioned)
    - self_medicated → infer from medicine_advised_by
    """
    extracted = state.get("extracted_data", {})
    missing = state.get("missing", [])
    
    # Define auto-fillable fields
    auto_fill_defaults = {
        "severity_hospitalized": "no",
        "severity_death": "no",
        "severity_no_daily_activity_effect": "yes",  # No effect on daily life
        "severity_affected_daily_activity": "no",
        "severity_other": "None",
        "past_disease_history": "None",
    }
    
    # Infer related fields based on existing data
    if "self_medicated" in missing and "medicine_advised_by" in extracted:
        if "doctor" in str(extracted["medicine_advised_by"]).lower():
            auto_fill_defaults["self_medicated"] = "no"
        else:
            auto_fill_defaults["self_medicated"] = "yes"
    
    # Infer medicine_advised_by from self_medicated
    if "medicine_advised_by" in missing and "self_medicated" in extracted:
        if str(extracted["self_medicated"]).lower() == "yes":
            auto_fill_defaults["medicine_advised_by"] = "self"
        elif str(extracted["self_medicated"]).lower() == "no":
            auto_fill_defaults["medicine_advised_by"] = "doctor"
    
    # If side effect is continuing, remove stop_date from missing (not applicable)
    if "side_effect_continuing" in extracted:
        if str(extracted["side_effect_continuing"]).lower() in ["yes", "true"]:
            if "side_effect_stop_date" in missing:
                missing.remove("side_effect_stop_date")
                extracted["side_effect_stop_date"] = None  # Not applicable, still ongoing
                print(f"[Auto-Fill] Removed side_effect_stop_date (side effect still continuing)")
    
    # Apply defaults
    fields_filled = []
    for field, default_value in auto_fill_defaults.items():
        if field in missing:
            extracted[field] = default_value
            missing.remove(field)
            fields_filled.append(field)
    
    if fields_filled:
        print(f"[Auto-Fill] Filled {len(fields_filled)} optional fields with defaults")
    
    state["extracted_data"] = extracted
    state["missing"] = missing
    
    return state


def _get_current_section_missing(state: dict) -> list:
    """
    Get missing fields from current and next section (lookahead).
    Returns ordered list of fields to collect next.
    """
    from app.schemas.conversation_state import SECTIONS_ORDER
    
    all_missing = state.get("missing", [])
    current_idx = state.get("current_section_index", 0)
    
    # Build ordered missing list
    ordered_missing = []
    
    # Current section first
    if current_idx < len(SECTIONS_ORDER):
        current_section = SECTIONS_ORDER[current_idx]
        ordered_missing.extend([f for f in current_section if f in all_missing])
    
    # Next section (lookahead to catch early mentions)
    if current_idx + 1 < len(SECTIONS_ORDER):
        next_section = SECTIONS_ORDER[current_idx + 1]
        ordered_missing.extend([f for f in next_section if f in all_missing])
    
    # Add remaining fields
    for field in all_missing:
        if field not in ordered_missing:
            ordered_missing.append(field)
    
    return ordered_missing[:10]  # Limit to prevent context overflow


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
    IMPROVED: Context builder with section progression.
    
    KEY CHANGES:
    1. Calls _advance_section_if_needed() before building prompt
    2. Uses ordered field list from _get_current_section_missing()
    3. Filters already_collected to only non-null values
    """

    # NEW: Advance section if current one is complete
    state = _advance_section_if_needed(state)
    
    # Get missing fields first
    all_missing = state.get("missing", [])
    
    # NEW: Check if case has sufficient data (even with missing optional fields)
    if _is_case_sufficient(state) and all_missing:
        # Auto-fill remaining optional fields
        state = _auto_fill_optional_fields(state)
        all_missing = state.get("missing", [])  # Update after auto-fill
        print(f"[Completion] Case sufficient → Auto-filled optionals → {len(all_missing)} remaining")
    
    user_type = state.get("user_type")
    curr_msg = state.get("current_message", "")
    to_use = state.get("to_use", "")
    already = state.get("extracted_data", {})
    prev_msgs = state.get("chat_history", [])
    problems = state.get("problems", [])
    has_given_doc = state.get("doc_id") is not None
    LANGUAGE = state.get("language", "en")

    # Case complete check
    if not all_missing:
        state["case_complete"] = True
        case_id = state.get("case_id", "N/A")
        if user_type == "patient":
            return (
                f"🎉 *धन्यवाद!* सभी जानकारी मिल गई है।\n\n"
                f"📋 *आपका Case ID:*\n`{case_id}`\n\n"
                f"✅ Case सफलतापूर्वक सेव हो गया है।\n\n"
                f"💾 Iss Case ID ko save karke rakhein - iske zariye aap baad mein apna case resume kar sakte hain।"
            ) if LANGUAGE == "hi" else (
                f"🎉 *Thank you!* All information received.\n\n"
                f"📋 *Your Case ID:*\n`{case_id}`\n\n"
                f"✅ Case saved successfully.\n\n"
                f"💾 Save this Case ID - you can use it to resume your case later."
            )
        else:
            return (
                f"✅ *Case Complete*\n\n"
                f"All required clinical information has been collected.\n\n"
                f"📋 *Case ID:* `{case_id}`\n\n"
                f"Case submitted successfully to the PV system."
            )

    # NEW: Get ordered missing fields using sections
    target_missing = _get_current_section_missing(state)
    
    # Build concise history
    concise_history = _build_concise_chat_history(prev_msgs, max_turns=3)
    
    # Format fields for display
    readable_missing = _format_field_names_for_display(target_missing)
    
    # NEW: Filter already_collected to only non-null values
    already_collected = {k: v for k, v in already.items() if v is not None}

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
                already_collected=list(already_collected.keys()),
                readable_missing=readable_missing,
                problems=problems
            )},
            {"role": "system", "content": f"User's current message: {curr_msg}"},
            {"role": "system", "content": f"Information already collected (DO NOT ask again):\n{already_collected}"},
            {"role": "system", "content": f"Recent conversation:\n{concise_history}"},
            {"role": "system", "content": f"IMPORTANT: The user is speaking {LANGUAGE}. You MUST reply in {LANGUAGE}."},
        ]
        
        if problems:
            messages.append({"role": "system", "content": f"Issues with current input: {', '.join(problems)}"})
        
        if has_given_doc:
            messages.append({"role": "system", "content": "User has already provided a document/prescription."})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,  # Slightly higher for Llama
            max_tokens=100    # Force concise responses
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
                already_collected=list(already_collected.keys()),
                readable_missing=readable_missing
            )},
            {"role": "system", "content": f"Provider's message: {curr_msg}"},
            {"role": "system", "content": f"Data collected:\n{already_collected}"},
            {"role": "system", "content": f"Recent exchange:\n{concise_history}"},
            {"role": "system", "content": f"IMPORTANT: The doctor is speaking {LANGUAGE}. You MUST reply in {LANGUAGE}."},
        ]
        
        if problems:
            messages.append({"role": "system", "content": f"Technical issues: {', '.join(problems)}"})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=100
        )

        output = response.choices[0].message.content.strip()
        return output

    else:
        return "Please tell me if you are a Patient or a Doctor."