# backend/app/agents/pv_followup_agent.py
"""
PV Follow-up Agent - FIXED VERSION
Key improvements:
1. Proper problems list reset
2. Better validation logic
3. Language detection
4. Cleaner state management
5. Debug logging for extraction progress
"""

from app.services.load_data import download_media
from app.services.ocr_service import run_ocr_on_state
from app.services.stt_service import run_voice_on_state
from app.services.see_useless import see_useless_yes
from app.services.fill_data import fill_data_remove_missing
from app.utils.context_builder import build_llm_messages
from app.services.llm_service import get_model
from app.services.convert_lang_msg import convert_to_language


def _detect_language(text: str) -> str:
    """
    LLM-only language detection using get_model().
    Separates Hindi (Devanagari) and Hinglish (Roman Hindi).
    """

    if not text or not text.strip():
        return "en"

    client, model = get_model()

    system_prompt = (
        "You are a strict language detection engine.\n\n"
        "Identify the language of the user's message and reply with ONLY ONE code from below:\n\n"
        "hi     = Hindi written in Devanagari script\n"
        "hi_en  = Hinglish (Hindi written in English/Roman letters)\n"
        "en     = English\n"
        "ta     = Tamil\n"
        "te     = Telugu\n"
        "bn     = Bengali\n"
        "mr     = Marathi\n"
        "gu     = Gujarati\n"
        "ur     = Urdu\n"
        "pa     = Punjabi\n\n"
        "Rules:\n"
        "- Respond with ONLY the language code\n"
        "- No explanation\n"
        "- No extra text\n"
        "- If unsure, respond with en"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=5
        )

        lang = response.choices[0].message.content.strip().lower()

        allowed_langs = {
            "hi", "hi_en", "en", "ta", "te", "bn", "mr", "gu", "ur", "pa"
        }

        return lang if lang in allowed_langs else "en"

    except Exception:
        return "en"



def run_pv_followup_agent(state: dict) -> dict:
    """
    IMPROVED agent with better state management and validation.
    
    KEY CHANGES:
    1. Added debug logging for extraction progress
    2. Trim chat history to prevent bloat
    3. Track missing count before/after extraction
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
            lang = state.get("language", "en")
            if state.get("doc_id"):
                # SKIP OCR for license - Just accept it
                state["verified_doctor"] = True
                state["followup_msg"] = convert_to_language("Your license has been received. You may now proceed to report the case.", lang)
                return state
            else:
                state["followup_msg"] = convert_to_language("Please upload your medical license ID to verify your identity.", lang)
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
            
            # NEW: Track extraction progress
            missing_before = len(state.get("missing", []))
            
            # Extract data and generate response
            state = fill_data_remove_missing(state)
            
            # NEW: Log progress
            missing_after = len(state.get("missing", []))
            if missing_after < missing_before:
                print(f"[Agent] ✓ Progress: {missing_before} → {missing_after} fields remaining")
            
            # Update chat history - store ONLY user content, not assistant responses
            if "chat_history" not in state:
                state["chat_history"] = []
            
            if state["to_use"]:
                state["chat_history"].append({"role": "user", "content": state["to_use"]})
            
            # Generate follow-up
            followup = build_llm_messages(state)
            
            # Only store assistant message if it's an actual question
            if followup and followup != "NO_FOLLOWUP":
                # NEW: Trim history to prevent bloat
                if len(state["chat_history"]) > 10:
                    state["chat_history"] = state["chat_history"][-10:]
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
                state["problems"].append(convert_to_language("I didn't quite understand that. Could you please rephrase?", lang))
            else:
                to_use.append(state["current_message"])

        # Photo validation
        if state.get("doc_id"):
            doc_text = state.get("current_doc_data", {}).get("raw_text", "")
            if doc_text:
                photo_use = see_useless_yes(doc_text, missing)
                if photo_use is True:
                    lang = state.get("language", "en")
                    state["problems"].append(convert_to_language("I couldn't read the document clearly. Please upload a clearer image.", lang))
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
                    state["problems"].append(convert_to_language("The audio wasn't clear. Could you please try again?", lang))
                else:
                    to_use.append(voice_text)
                    if "voice_all" not in state:
                        state["voice_all"] = []
                    state["voice_all"].append(voice_text)

        state["to_use"] = " ".join(to_use)

        # NEW: Track extraction progress
        missing_before = len(state.get("missing", []))

        # Extract data and generate response
        state = fill_data_remove_missing(state)
        
        # NEW: Log progress
        missing_after = len(state.get("missing", []))
        if missing_after < missing_before:
            print(f"[Agent] ✓ Progress: {missing_before} → {missing_after} fields remaining")
        
        # Update chat history
        if "chat_history" not in state:
            state["chat_history"] = []
        
        if state["to_use"]:
            state["chat_history"].append({"role": "user", "content": state["to_use"]})
        
        # Generate follow-up
        followup = build_llm_messages(state)
        
        # Only store assistant message if it's an actual question
        if followup and followup != "NO_FOLLOWUP":
            # NEW: Trim history to prevent bloat
            if len(state["chat_history"]) > 10:
                state["chat_history"] = state["chat_history"][-10:]
            state["chat_history"].append({"role": "assistant", "content": followup})
        
        state["followup_msg"] = followup

        return state
    
    # =========================================
    # FALLBACK
    # =========================================
    else:
        state["followup_msg"] = "Please tell me if you are a Patient or a Doctor."
        return state