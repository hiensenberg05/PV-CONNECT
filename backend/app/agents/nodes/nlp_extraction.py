import json
from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def extract_data_node(state: CaseState) -> CaseState:
    model = get_model()
    text = state.get("current_message", "")
    language = state.get("language", "en")
    prompt = f"""
    Extract adverse event details from the message below.
    Language: {language}
    Message: "{text}"
    Return JSON with keys: drug_name, symptoms (list), severity, start_date, dosage.
    If missing, set null.
    """
    response = model.generate_content(prompt)
    try:
        extracted = json.loads(response.text)
    except Exception:
        extracted = {}

    state.setdefault("extracted_data", {})
    for key, value in extracted.items():
        if value:
            state["extracted_data"][key] = value
    return state
