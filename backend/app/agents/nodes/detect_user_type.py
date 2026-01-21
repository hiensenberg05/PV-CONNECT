from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def detect_user_type_node(state: CaseState) -> CaseState:
    model = get_model()
    text = state.get("current_message", "")
    prompt = (
        "Classify the sender as 'patient' or 'doctor' based on the message. "
        "Return JSON {\"user_type\": \"patient\"}. Message: "
        f"\"{text}\""
    )
    response = model.generate_content(prompt)
    state["user_type"] = response.text.strip().lower() if response.text else "patient"
    return state
