# backend/app/agents/pv_followup_agent.py
"""
PV Follow-up Agent.
Restored logic with strict input validation using see_useless.

This agent is called AFTER workflow handles:
- User type detection
- Initial doctor verification check

Agent responsibilities:
1. Process media (OCR for docs, STT for voice)
2. Validate input usefulness via see_useless
3. Extract data from useful inputs only
4. Populate problems list for useless inputs
5. Generate follow-up question via LLM
"""

from app.services.load_data import download_media
from app.services.ocr_service import run_ocr_on_state
from app.services.stt_service import run_voice_on_state
from app.services.see_useless import see_useless_yes
from app.services.fill_data import fill_data_remove_missing
from app.utils.context_builder import build_llm_messages


def run_pv_followup_agent(state: dict) -> dict:
    """
    LLM-FIRST agent with strict validation logic.
    Python does minimal decision making beyond usefulness checks.
    """

    user_type = state.get("user_type")

    # =========================================
    # DOCTOR FLOW
    # =========================================
    if user_type == "doctor":
        
        # Unverified doctor - handle license submission
        if not state.get("verified_doctor"):
            if state.get("doc_id"):
                # Doctor sent a document (license)
                try:
                    media = download_media(state["doc_id"])
                    state = run_ocr_on_state(state, media["file_path"])
                    doc_text = state.get("current_doc_data", {}).get("raw_text", "")
                    
                    if doc_text and len(doc_text) > 5:
                        state["verified_doctor"] = True
                        state["followup_msg"] = "Your license has been received. You may now proceed to report the case."
                        return state
                    else:
                        state["verified_doctor"] = False
                        state["followup_msg"] = "Could not read your license. Please upload a clear image."
                        return state
                except Exception:
                    state["followup_msg"] = "Error processing license. Please try again."
                    return state
            else:
                state["followup_msg"] = "Please upload your medical license ID to verify your identity."
                return state
        
        # Verified Doctor - Normal data collection flow
        elif state.get("verified_doctor") is True:
            # Process Media
            if state.get("doc_id"):
                try:
                    media = download_media(state["doc_id"])
                    state = run_ocr_on_state(state, media["file_path"])
                except Exception:
                    pass
            
            if state.get("voice_id"):
                try:
                    media = download_media(state["voice_id"])
                    state = run_voice_on_state(state, media["file_path"])
                except Exception:
                    pass

            # Check Usefulness of each input
            missing = state.get("missing", [])
            text_use = see_useless_yes(state.get("current_message", ""), missing)
            photo_use = see_useless_yes(state.get("current_doc_data", {}).get("raw_text", ""), missing)
            voice_use = see_useless_yes(state.get("current_voice_data", {}).get("transcript", ""), missing)
            
            problems = []
            to_use = []

            # Text validation
            if text_use is True and state.get("current_message", ""):
                problems.append("The message does not contain relevant clinical information.")
            else:
                msg = state.get("current_message", "")
                if msg:
                    to_use.append(msg)

            # Photo validation
            if photo_use is True and state.get("doc_id"):
                problems.append("The document does not contain useful clinical data.")
            else:
                doc_text = state.get("current_doc_data", {}).get("raw_text", "")
                if doc_text:
                    to_use.append(doc_text)
                    if "doc_all" not in state:
                        state["doc_all"] = []
                    state["doc_all"].append(doc_text)

            # Voice validation
            if voice_use is True and state.get("voice_id"):
                problems.append("The voice message was unclear or irrelevant.")
            else:
                voice_text = state.get("current_voice_data", {}).get("transcript", "")
                if voice_text:
                    to_use.append(voice_text)
                    if "voice_all" not in state:
                        state["voice_all"] = []
                    state["voice_all"].append(voice_text)
            
            state["problems"] = problems
            state["to_use"] = " ".join(to_use)
            
            # Extract data and generate response
            state = fill_data_remove_missing(state)
            
            if "chat_history" not in state:
                state["chat_history"] = []
            state["chat_history"].append({"role": "user", "content": state["to_use"]})
            
            messages = build_llm_messages(state)
            state["chat_history"].append({"role": "assistant", "content": messages})
            state["followup_msg"] = messages
            
            return state

    # =========================================
    # PATIENT FLOW
    # =========================================
    elif user_type == "patient":
        # Process Media
        if state.get("doc_id"):
            try:
                media = download_media(state["doc_id"])
                state = run_ocr_on_state(state, media["file_path"])
            except Exception:
                pass
        
        if state.get("voice_id"):
            try:
                media = download_media(state["voice_id"])
                state = run_voice_on_state(state, media["file_path"])
            except Exception:
                pass

        # Check Usefulness of each input
        missing = state.get("missing") if state.get("missing") else []
        
        text_use = see_useless_yes(state.get("current_message", ""), missing)
        photo_use = see_useless_yes(state.get("current_doc_data", {}).get("raw_text", ""), missing)
        voice_use = see_useless_yes(state.get("current_voice_data", {}).get("transcript", ""), missing)
        
        problems = []
        to_use = []

        # Text validation
        if text_use is True and state.get("current_message", ""):
            problems.append("Aapke message mein kuch useful information nahi hai.")
        else:
            msg = state.get("current_message", "")
            if msg:
                to_use.append(msg)

        # Photo validation
        if photo_use is True and state.get("doc_id"):
            problems.append("Aapke photo/document mein kuch useful information nahi hai.")
        else:
            doc_text = state.get("current_doc_data", {}).get("raw_text", "")
            if doc_text:
                to_use.append(doc_text)
                if "doc_all" not in state:
                    state["doc_all"] = []
                state["doc_all"].append(doc_text)

        # Voice validation
        if voice_use is True and state.get("voice_id"):
            problems.append("Aapke voice message mein kuch useful information nahi hai.")
        else:
            voice_text = state.get("current_voice_data", {}).get("transcript", "")
            if voice_text:
                to_use.append(voice_text)
                if "voice_all" not in state:
                    state["voice_all"] = []
                state["voice_all"].append(voice_text)

        state["problems"] = problems
        state["to_use"] = " ".join(to_use)

        # Extract data and generate response
        state = fill_data_remove_missing(state)
        
        if "chat_history" not in state:
            state["chat_history"] = []
        state["chat_history"].append({"role": "user", "content": state["to_use"]})
        
        messages = build_llm_messages(state)
        state["chat_history"].append({"role": "assistant", "content": messages})
        state["followup_msg"] = messages

        return state
    
    # =========================================
    # FALLBACK
    # =========================================
    else:
        state["followup_msg"] = "Please tell me if you are a Patient or a Doctor."
        return state