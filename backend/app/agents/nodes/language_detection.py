from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def detect_language_node(state: CaseState) -> CaseState:
    model = get_model()
    text = state.get("current_message", "")
    prompt = f'Detect ISO language code only for: "{text}". Return JSON {{"language": "en"}}'
    response = model.generate_content(prompt)
    state["language"] = response.text.strip().lower()[:2] or "en"
    return state
