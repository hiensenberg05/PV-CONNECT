from app.services.mongodb_service import get_db
from app.agents.state import CaseState


async def verify_doctor_node(state: CaseState) -> CaseState:
    db = get_db()
    phone = state.get("phone_number")
    doctor = db.users.find_one({"phone_number": phone, "user_type": "doctor", "verified": True})
    if doctor:
        state["doctor_verified"] = True
        return state
    state["awaiting_license"] = True
    state["next_question"] = "Please upload your medical license for verification."
    return state
