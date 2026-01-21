from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def generate_followup_node(state: CaseState) -> CaseState:
    model = get_model()
    missing = state.get("missing_fields", ["details"])[0]
    language = state.get("language", "en")
    prompt = f"""
    Ask one friendly, short question in {language} to collect: {missing}.
    Return plain text only.
    """
    response = model.generate_content(prompt)
    state["next_question"] = response.text.strip()
    return state
