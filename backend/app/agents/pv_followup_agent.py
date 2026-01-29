
# {
#   "patient_name": null,
#   "patient_gender": null,
#   "patient_age_value": null,
#   "patient_age_unit": null,

#   "reason_for_medicine": null,
#   "medicine_advised_by": null,
#   "self_medicated": null,
#   "past_disease_history": null,

#   "medicine_name": null,
#   "medicine_quantity_taken": null,
#   "medicine_dosage_form": null,
#   "medicine_expiry_date": null,
#   "medicine_start_date": null,
#   "medicine_stop_date": null,

#   "side_effect_start_date": null,
#   "side_effect_continuing": null,
#   "side_effect_stop_date": null,

#   "severity_no_daily_activity_effect": false,
#   "severity_affected_daily_activity": false,
#   "severity_hospitalized": false,
#   "severity_death": false,
#   "severity_other": null,

#   "side_effect_description": null,
#   "management_action_taken": null
# }


# [
#   "patient_name",
#   "patient_gender",
#   "patient_age_value",
#   "patient_age_unit",

#   "reason_for_medicine",
#   "medicine_advised_by",
#   "self_medicated",
#   "past_disease_history",

#   "medicine_name",
#   "medicine_quantity_taken",
#   "medicine_dosage_form",
#   "medicine_expiry_date",
#   "medicine_start_date",
#   "medicine_stop_date",

#   "side_effect_start_date",
#   "side_effect_continuing",
#   "side_effect_stop_date",

#   "severity_no_daily_activity_effect",
#   "severity_affected_daily_activity",
#   "severity_hospitalized",
#   "severity_death",
#   "severity_other",

#   "side_effect_description",
#   "management_action_taken"
# ]




from services.load_data import download_media
from services.ocr_service import run_ocr_on_state
from services.stt_service import run_voice_on_state
from services.llm_service import get_model
# from services.verify_license import verify
from utils.context_builder import build_llm_messages
from services.see_useless import see_useless_yes
from services.fill_data import fill_data_remove_missing


def run_pv_followup_agent(state: dict) -> dict:
    """
    LLM-FIRST agent.
    Python does ZERO decision making.
    I will only get is user patient or doctor and the language of the msg.
    """

    if state.get("user_type") == "doctor":
        if state.get("verified_doctor") == None or state["verified_doctor"] is False:
            if state.get("doc_id"):
                media = download_media(state["doc_id"])
                state = run_ocr_on_state(state, media["file_path"])
                is_doctor = verify(state["current_doc_data"]["raw_text"])
                if is_doctor:
                    state["verified_doctor"] = True
                    state["followup_msg"]=("Aapka license verify ho gaya hai. Ab aap aage badh sakte hain.")
                    return state
                else:
                    state["verified_doctor"] = False
                    state["followup_msg"]=("Bsdk apni id daal. And shand kuch mat daal.")
                    return state
            else:
                state["followup_msg"]=("Bsdk id daal apni.")
                return state
        elif state["verified_doctor"] is True:
            if state.get("doc_id"):
                media = download_media(state["doc_id"])
                state = run_ocr_on_state(state, media["file_path"])
            if state.get("voice_id"):
                media = download_media(state["voice_id"])
                state = run_voice_on_state(state, media["file_path"])
            text_use=see_useless_yes(state.get("current_message",""),state["missing"])
            photo_use=see_useless_yes(state.get("current_doc_data",{}).get("raw_text",""),state["missing"])
            voice_use=see_useless_yes(state.get("current_voice_data",{}).get("transcript",""),state["missing"])
            problems = []
            to_use=[]
            if text_use is True and state.get("current_message","")!="":
                problems.append("Aapke message mein kuch useful information nahi hai.")
            else:
                to_use.append(state.get("current_message",""))
            if photo_use is True and state.get("doc_id"):
                problems.append("Aapke photo/document mein kuch useful information nahi hai.")
            else:
                to_use.append(state.get("current_doc_data",{}).get("raw_text",""))
                state["doc_all"].append(state.get("current_doc_data",{}).get("raw_text",""))
            if voice_use is True and state.get("voice_id"):
                problems.append("Aapke voice message mein kuch useful information nahi hai.")
            else:
                to_use.append(state.get("current_voice_data",{}).get("transcript",""))
                state["voice_all"].append(state.get("current_voice_data",{}).get("transcript",""))
            state["problems"]=problems
            state["to_use"]=" ".join(to_use)
            state=fill_data_remove_missing(state)
            state["chat_history"].append({"role": "user", "content": state["to_use"]})
            messages = build_llm_messages(state)
            state["chat_history"].append({"role": "assistant", "content": messages})

            state["followup_msg"] = messages
            return state
        
    elif state.get("user_type") == "patient":
        if state.get("doc_id"):
                media = download_media(state["doc_id"])
                state = run_ocr_on_state(state, media["file_path"])
        if state.get("voice_id"):
            media = download_media(state["voice_id"])
            state = run_voice_on_state(state, media["file_path"])
        text_use=see_useless_yes(state.get("current_message",""),state.get("missing",[]))
        photo_use=see_useless_yes(state.get("current_doc_data",{}).get("raw_text",""),state.get("missing",[]))
        voice_use=see_useless_yes(state.get("current_voice_data",{}).get("transcript",""),state.get("missing",[]))
        problems = []
        to_use=[]
        if text_use is True and state.get("current_message","")!="":
            problems.append("Aapke message mein kuch useful information nahi hai.")
        else:
            to_use.append(state.get("current_message",""))
        if photo_use is True and state.get("curr_doc_id"):
            problems.append("Aapke photo/document mein kuch useful information nahi hai.")
        else:
            to_use.append(state.get("current_doc_data",{}).get("raw_text",""))
        if voice_use is True and state.get("curr_voice_id"):
            problems.append("Aapke voice message mein kuch useful information nahi hai.")
        else:
            to_use.append(state.get("current_voice_data",{}).get("transcript",""))
        state["problems"]=problems
        state["to_use"]=" ".join(to_use)
        state=fill_data_remove_missing(state)
        state["chat_history"].append({"role": "user", "content": state["to_use"]})
        messages = build_llm_messages(state)
        state["chat_history"].append({"role": "assistant", "content": messages})
        state["followup_msg"] = messages

        return state

            



# state mein case_completed true hai to case band
# add all feilds above and set to null in extracted data
# missing mein upar ka list bhar de

# add in stae doc_all and voice_all