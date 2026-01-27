# import json
# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# async def extract_data_node(state: CaseState) -> CaseState:
#     model = get_model()
#     text = state.get("current_message", "")
#     language = state.get("language", "en")
#     prompt = f"""
#     Extract adverse event details from the message below.
#     Language: {language}
#     Message: "{text}"
#     Return JSON with keys: drug_name, symptoms (list), severity, start_date, dosage.
#     If missing, set null.
#     """
#     response = model.generate_content(prompt)
#     try:
#         extracted = json.loads(response.text)
#     except Exception:
#         extracted = {}

#     state.setdefault("extracted_data", {})
#     for key, value in extracted.items():
#         if value:
#             state["extracted_data"][key] = value
#     return state


import json
import re
from app.services.gemini_service import get_model   # groq-backed
from app.agents.state import CaseState


def _safe_json_parse(text: str) -> dict:
    """
    Extract JSON even if model wraps it in ```json ... ```
    """
    if not text:
        return {}

    # remove code fences
    text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    try:
        return json.loads(text)
    except Exception:
        return {}


async def extract_data_node(state: CaseState) -> CaseState:
    model = get_model()

    text = state.get("current_message", "")
    language = state.get("language", "en")

    prompt = f"""
        You are a medical information extraction system.

        Extract adverse event information from the message below.

        Language: {language}

        Message:
        {text}

        Return ONLY valid JSON.
        Do NOT add explanations.
        Do NOT wrap in markdown.

        JSON schema:
        {{
        "drug_name": string | null,
        "symptoms": list[string] | null,
        "severity": "mild" | "moderate" | "severe" | null,
        "start_date": string | null,
        "dosage": string | null,
        "has_medi_bill": boolean | null
        }}
        """

    response = model.generate_content(prompt)
    raw = response.text if response else ""

    extracted = _safe_json_parse(raw)

    # ensure dict exists
    state.setdefault("extracted_data", {})

    # merge non-null values
    for key in ["drug_name", "symptoms", "severity", "start_date", "dosage","has_medi_bill"]:
        value = extracted.get(key)
        if value not in (None, "", [], {}):
            state["extracted_data"][key] = value

    if state.get("has_medi_bill") is None:
        state["has_medi_bill"] = extracted.get("has_medi_bill")

    return state


