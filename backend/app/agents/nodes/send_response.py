from app.channels.whatsapp import send_whatsapp_message
from app.agents.state import CaseState


async def send_response_node(state: CaseState) -> CaseState:
    phone = state.get("phone_number")
    text = state.get("next_question") or "Thank you, your report is recorded."
    if phone:
        await send_whatsapp_message(phone, text)
    state["response_sent"] = True
    return state
