# backend/app/agents/pv_followup_agent.py
"""
PV Follow-up Agent - FIXED VERSION
Key improvements:
1. Proper problems list reset
2. Better validation logic
3. Language detection
4. Cleaner state management
"""

from app.services.load_data import download_media
from app.services.ocr_service import run_ocr_on_state
from app.services.stt_service import run_voice_on_state
from app.services.see_useless import see_useless_yes
from app.services.fill_data import fill_data_remove_missing
from app.utils.context_builder import build_llm_messages


def _detect_language(text: str) -> str:
    """
    Simple language detection - checks for Hindi/Hinglish patterns.
    Returns 'hi' for Hindi/Hinglish, 'en' for English.
    """
    if not text:
        return "en"
    
    # Common Hindi/Hinglish words
    hindi_markers = [
        'mujhe', 'mera', 'mere', 'hain', 'hai', 'kya', 'kaise', 'kaun',
        'aap', 'tum', 'main', 'hum', 'ye', 'wo', 'nahi', 'haan',
        'dawai', 'dawa', 'goli', 'tablet', 'bukhar', 'dard', 'pet'
    ]
    
    text_lower = text.lower()
    hindi_count = sum(1 for marker in hindi_markers if marker in text_lower)
    
    return "hi" if hindi_count >= 2 else "en"


def run_pv_followup_agent(state: dict) -> dict:
    """
    IMPROVED agent with better state management and validation.
    """
    
    # ALWAYS initialize problems at the start
    if "problems" not in state:
        state["problems"] = []

    user_type = state.get("user_type")
    
    # Detect and update language
    curr_msg = state.get("current_message", "")
    if curr_msg:
        detected_lang = _detect_language(curr_msg)
        state["language"] = detected_lang

    # =========================================
    # DOCTOR FLOW
    # =========================================
    if user_type == "doctor":
        
        # Unverified doctor - handle license submission
        if not state.get("verified_doctor"):
            if state.get("doc_id"):
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
            # RESET problems list for this turn
            state["problems"] = []
            
            # Process Media
            if state.get("doc_id"):
                try:
                    media = download_media(state["doc_id"])
                    state = run_ocr_on_state(state, media["file_path"])
                except Exception as e:
                    state["problems"].append(f"Error processing document: {str(e)}")
            
            if state.get("voice_id"):
                try:
                    media = download_media(state["voice_id"])
                    state = run_voice_on_state(state, media["file_path"])
                except Exception as e:
                    state["problems"].append(f"Error processing voice: {str(e)}")

            # Check Usefulness of each input
            missing = state.get("missing", [])
            to_use = []

            # Text validation
            if state.get("current_message"):
                text_use = see_useless_yes(state["current_message"], missing)
                if text_use is True:
                    state["problems"].append("The message does not contain relevant clinical information.")
                else:
                    to_use.append(state["current_message"])

            # Photo validation
            if state.get("doc_id"):
                doc_text = state.get("current_doc_data", {}).get("raw_text", "")
                if doc_text:
                    photo_use = see_useless_yes(doc_text, missing)
                    if photo_use is True:
                        state["problems"].append("The document does not contain useful clinical data.")
                    else:
                        to_use.append(doc_text)
                        if "doc_all" not in state:
                            state["doc_all"] = []
                        state["doc_all"].append(doc_text)

            # Voice validation
            if state.get("voice_id"):
                voice_text = state.get("current_voice_data", {}).get("transcript", "")
                if voice_text:
                    voice_use = see_useless_yes(voice_text, missing)
                    if voice_use is True:
                        state["problems"].append("The voice message was unclear or irrelevant.")
                    else:
                        to_use.append(voice_text)
                        if "voice_all" not in state:
                            state["voice_all"] = []
                        state["voice_all"].append(voice_text)
            
            state["to_use"] = " ".join(to_use)
            
            # Extract data and generate response
            state = fill_data_remove_missing(state)
            
            # Update chat history - store ONLY user content, not assistant responses
            if "chat_history" not in state:
                state["chat_history"] = []
            
            if state["to_use"]:
                state["chat_history"].append({"role": "user", "content": state["to_use"]})
            
            # Generate follow-up
            followup = build_llm_messages(state)
            
            # Only store assistant message if it's an actual question
            if followup and followup != "NO_FOLLOWUP":
                state["chat_history"].append({"role": "assistant", "content": followup})
            
            state["followup_msg"] = followup
            
            return state

    # =========================================
    # PATIENT FLOW
    # =========================================
    elif user_type == "patient":
        # RESET problems list for this turn
        state["problems"] = []
        
        # Process Media
        if state.get("doc_id"):
            try:
                media = download_media(state["doc_id"])
                state = run_ocr_on_state(state, media["file_path"])
            except Exception as e:
                state["problems"].append(f"Error processing document: {str(e)}")
        
        if state.get("voice_id"):
            try:
                media = download_media(state["voice_id"])
                state = run_voice_on_state(state, media["file_path"])
            except Exception as e:
                state["problems"].append(f"Error processing voice: {str(e)}")

        # Check Usefulness of each input
        missing = state.get("missing", [])
        to_use = []

        # Text validation
        if state.get("current_message"):
            text_use = see_useless_yes(state["current_message"], missing)
            if text_use is True:
                lang = state.get("language", "en")
                msg = "Mujhe samajh nahi aaya." if lang == "hi" else "I didn't quite get that."
                state["problems"].append(msg)
            else:
                to_use.append(state["current_message"])

        # Photo validation
        if state.get("doc_id"):
            doc_text = state.get("current_doc_data", {}).get("raw_text", "")
            if doc_text:
                photo_use = see_useless_yes(doc_text, missing)
                if photo_use is True:
                    lang = state.get("language", "en")
                    msg = "Document clearly nahi dikh raha." if lang == "hi" else "I couldn't read the document clearly."
                    state["problems"].append(msg)
                else:
                    to_use.append(doc_text)
                    if "doc_all" not in state:
                        state["doc_all"] = []
                    state["doc_all"].append(doc_text)

        # Voice validation
        if state.get("voice_id"):
            voice_text = state.get("current_voice_data", {}).get("transcript", "")
            if voice_text:
                voice_use = see_useless_yes(voice_text, missing)
                if voice_use is True:
                    lang = state.get("language", "en")
                    msg = "Voice saaf nahi thi." if lang == "hi" else "The audio wasn't clear."
                    state["problems"].append(msg)
                else:
                    to_use.append(voice_text)
                    if "voice_all" not in state:
                        state["voice_all"] = []
                    state["voice_all"].append(voice_text)

        state["to_use"] = " ".join(to_use)

        # Extract data and generate response
        state = fill_data_remove_missing(state)
        
        # Update chat history
        if "chat_history" not in state:
            state["chat_history"] = []
        
        if state["to_use"]:
            state["chat_history"].append({"role": "user", "content": state["to_use"]})
        
        # Generate follow-up
        followup = build_llm_messages(state)
        
        # Only store assistant message if it's an actual question
        if followup and followup != "NO_FOLLOWUP":
            state["chat_history"].append({"role": "assistant", "content": followup})
        
        state["followup_msg"] = followup

        return state
    
    # =========================================
    # FALLBACK
    # =========================================
    else:
        state["followup_msg"] = "Please tell me if you are a Patient or a Doctor."
        return state