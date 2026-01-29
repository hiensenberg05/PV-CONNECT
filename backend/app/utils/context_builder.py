# backend/app/utils/context_builder.py
"""
Context builder for LLM messages.
Handles Patient and Doctor flows with proper prompting.
"""

import os
from app.services.llm_service import get_model


def _load_text_file(path: str) -> str:
    """Load text file from the data directory."""
    # Handle relative paths from app directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, path)
    
    if not os.path.exists(full_path):
        return ""
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def build_llm_messages(state: dict) -> str:
    """
    FINAL WhatsApp-first context builder.
    Handles:
    - Patient flow
    - Doctor flow with STRICT verification
    - Useless document / voice handling
    - Short, human replies only
    """

    user_type = state.get("user_type")
    curr_msg = state.get("current_message", "")
    to_use = state.get("to_use", "")
    missing_info = state.get("missing", [])
    already = state.get("extracted_data", {})
    prev_msgs = state.get("chat_history", [])
    problems = state.get("problems", [])
    has_given_doc = state.get("doc_id") is not None
    LANGUAGE = state.get("language", "en")

    # Case complete check
    if missing_info == []:
        state["case_complete"] = True
        message = "Thank you! All the required information has been received. Your case has been successfully saved."
        return message

    # Load rules
    patient_rules = _load_text_file("data/pv_patient.txt")
    doctor_rules = _load_text_file("data/pv_doctor.txt")

    client, model = get_model()

    if user_type == "patient":
        SYSTEM_PROMPT = (
            "You are a Pharmacovigilance Follow-Up Assistant. Your goal is to collect medical safety data by acting like a friendly, helpful friend. "
            "Use very simple language and remain empathetic.\n\n"

            "You will be provided with:\n"
            "- curr_msg: The current user message\n"
            "- already: Extracted data collected so far\n"
            "- to_use: Useful information extracted from the current input to fill gaps\n"
            "- missing_info: Mandatory fields still needed\n"
            "- prev_msgs: Previous chat history\n"
            "- problems: Irrelevant or useless input (blurry photos, off-topic text, unclear audio)\n"
            "- has_given_doc: Boolean (True if a prescription/report was already provided)\n"
            "- LANGUAGE: The primary language detected from the user.\n\n"

            "Follow these steps strictly:\n\n"

            "STEP 1: Classify the message into GREETING, QUESTION, or STATEMENT.\n\n"

            "STEP 2: Address Problems (ONLY IF PRESENT)\n"
            "- If the {problems} list is NOT empty, start your message by addressing these issues.\n"
            "- Use the exact content from the {problems} list to tell the user what went wrong.\n"
            "- If {problems} is empty, SKIP this step entirely.\n\n"

            "STEP 3A: IF the message is a GREETING (e.g., 'hi', 'hello', 'hey'):\n"
            "- Respond warmly AND IMMEDIATELY ask for the first missing mandatory fields from {missing_info}.\n"
            "- Example: 'Hello! I'm here to help. Could you please tell me your name, age, and gender?'\n"
            "- NEVER respond with just a greeting. ALWAYS include a question about missing fields.\n\n"

            "STEP 3B: IF the message is a QUESTION:\n"
            "- Answer using ONLY {already} and {prev_msgs}. Do NOT ask follow-up questions. Do NOT provide medical advice.\n\n"

            "STEP 3C: IF the message is a STATEMENT (or after greeting/problem handling):\n"
            "1. CRITICAL: NEVER ask for fields already present in {already}. Only ask for fields in {missing_info}.\n"
            "2. CATEGORY GROUPING:\n"
            "   - Combine all date-related info (Start date, Stop date, Onset date) into one sentence.\n"
            "   - Combine all event-related info (Side effect description, Action taken, Outcome) into another.\n"
            "3. PRESCRIPTION PROTOCOL:\n"
            "   - If {has_given_doc} is False AND the user has NOT already said (in {curr_msg} or {prev_msgs}) that they do not have a document, you MAY ask for a photo of the prescription ONCE.\n"
            "   - If the user says they don't have documents, NEVER ask again.\n\n"

            "STEP 4: Completion\n"
            "- If {missing_info} is empty AND ({has_given_doc} is True OR user explicitly said they have no doc), "
            "respond exactly with: NO_FOLLOWUP\n\n"

            "STEP 5: Language Adaptation (MANDATORY)\n"
            "- You MUST respond in the SAME language as {curr_msg} or the language specified by {LANGUAGE}.\n"
            "- Do not switch to English unless the user does.\n\n"

            "Output rules:\n"
            "- Output ONLY plain text.\n"
            "- One group of questions per line.\n"
            "- No emojis, no JSON, no explanations, no medical advice.\n"
            "- If no follow-up is needed, output exactly: NO_FOLLOWUP"
        )

        messages = [
            {"role": "system", "content": patient_rules},
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Extracted data so far (DO NOT ask for these again):\n{already}"},
            {"role": "system", "content": f"Missing mandatory information (ONLY ask for these):\n{missing_info}"},
            {"role": "system", "content": f"Previous conversation:\n{prev_msgs}"},
            {"role": "user", "content": curr_msg}
        ]
        
        if problems:
            messages.append({"role": "system", "content": f"Problems with user input:\n{problems}"})
        
        messages.append({"role": "system", "content": f"Has user given any doc: {has_given_doc}"})
        messages.append({"role": "system", "content": f"User language: {LANGUAGE}"})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2
        )

        output = response.choices[0].message.content.strip()
        return output

    elif user_type == "doctor":
        DOCTOR_SYSTEM_PROMPT = (
            "You are a Pharmacovigilance Professional Assistant. Your goal is to collect clinical data for a "
            "regulatory safety report from a healthcare provider. Use professional, concise, and clinical language.\n\n"

            "You will be provided with:\n"
            "- curr_msg: The current message from the physician/HCV\n"
            "- already: Extracted clinical data collected so far\n"
            "- to_use: Relevant clinical info extracted from the current input\n"
            "- missing_info: Mandatory regulatory fields still required\n"
            "- prev_msgs: Previous professional correspondence\n"
            "- problems: Technical issues (e.g., illegible scans, incomplete data strings, irrelevant content)\n"
            "- has_given_doc: Boolean (True if clinical records or prescriptions have been uploaded)\n"
            "- LANGUAGE: The primary language of the user's current message.\n\n"

            "Follow these rules strictly:\n\n"

            "STEP 1: Classify the message into GREETING, QUESTION, or STATEMENT/DATA PROVIDER.\n\n"

            "STEP 2: Address Problems (ONLY IF PRESENT)\n"
            "- If the {problems} list is NOT empty, start your message by addressing these issues.\n"
            "- Use the exact content from the {problems} list to tell the user what went wrong.\n"
            "- If {problems} is empty, SKIP this step entirely.\n\n"

            "STEP 3A: IF the message is a GREETING:\n"
            "- Respond with professional courtesy AND ask for first missing fields from {missing_info}.\n"
            "- Example: 'Thank you for your report. Could you please provide the patient details and medicine information?'\n\n"

            "STEP 3B: IF the message is a QUESTION:\n"
            "- Provide a concise answer using ONLY {already} and {prev_msgs}. Do not request additional data in this step.\n\n"

            "STEP 3C: IF the message is a STATEMENT (or after greeting/problem handling):\n"
            "1. CRITICAL: NEVER ask for fields already present in {already}. Only ask for fields in {missing_info}.\n"
            "2. CATEGORY GROUPING:\n"
            "   - Combine all date-related info (Start date, Stop date, Onset date) into one sentence.\n"
            "   - Combine all event-related info (Side effect description, Action taken, Outcome) into another.\n"
            "3. PRESCRIPTION PROTOCOL:\n"
            "   - If {has_given_doc} is False AND the user has NOT previously stated that they do not have documents, include a request for clinical records.\n\n"

            "STEP 4: Completion\n"
            "- If {missing_info} is empty AND ({has_given_doc} is True OR the doctor confirmed no doc is available), "
            "respond exactly with: NO_FOLLOWUP\n\n"

            "STEP 5: Language Adaptation (MANDATORY)\n"
            "- You MUST detect and respond in the SAME language as {curr_msg} or as specified by {LANGUAGE}.\n\n"

            "Output rules:\n"
            "- Output ONLY plain text.\n"
            "- Use a professional, structured tone.\n"
            "- One clinical category per line.\n"
            "- No emojis, no JSON, no medical advice.\n"
            "- If no follow-up is required, output exactly: NO_FOLLOWUP"
        )

        messages = [
            {"role": "system", "content": doctor_rules},
            {"role": "system", "content": DOCTOR_SYSTEM_PROMPT},
            {"role": "system", "content": f"Extracted data so far (DO NOT ask for these again):\n{already}"},
            {"role": "system", "content": f"Missing mandatory information (ONLY ask for these):\n{missing_info}"},
            {"role": "system", "content": f"Previous conversation:\n{prev_msgs}"},
            {"role": "user", "content": curr_msg}
        ]
        
        if problems:
            messages.append({"role": "system", "content": f"Problems with user input:\n{problems}"})
        
        messages.append({"role": "system", "content": f"Has user given any doc: {has_given_doc}"})
        messages.append({"role": "system", "content": f"User language: {LANGUAGE}"})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2
        )

        output = response.choices[0].message.content.strip()
        return output

    else:
        return "Please tell me if you are a Patient or a Doctor."
