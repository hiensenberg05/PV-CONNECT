# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# async def detect_user_type_node(state: CaseState) -> CaseState:
#     model = get_model()
#     text = state.get("current_message", "")
#     prompt = (
#         "Classify the sender as 'patient' or 'doctor' based on the message. "
#         "Return JSON {\"user_type\": \"patient\"}. Message: "
#         f"\"{text}\""
#     )
#     response = model.generate_content(prompt)
#     state["user_type"] = response.text.strip().lower() if response.text else "patient"
#     return state


# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# async def detect_user_type_node(state: CaseState) -> CaseState:
#     model = get_model()
#     text = state.get("current_message", "")

#     prompt = (
#         "You are classifying the sender.\n"
#         "Reply with ONLY ONE WORD: patient OR doctor.\n\n"
#         f"Message: \"{text}\""
#     )

#     response = model.generate_content(prompt)
#     user_type = response.text.strip().lower()

#     state["user_type"] = user_type if user_type in ("patient", "doctor") else "patient"
#     return state


# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# async def detect_user_type_node(state: CaseState) -> CaseState:
#     model = get_model()
#     text = state.get("current_message", "")

#     prompt = f"""
# You are a medical message classification system.

# Classify WHO is sending the message:
# - patient
# - doctor

# Guidelines:
# - Patient messages are usually first-person ("I", "me", "my") and describe their own symptoms.
# - Doctor messages are usually third-person ("patient", "he", "she") and use clinical or professional language,
#   often mentioning diagnosis, dosage, frequency, or dates.

# Rules:
# - If the message talks about "the patient" as a separate person, classify as doctor.
# - If the sender describes their own symptoms, classify as patient.
# - If unclear, choose the most likely option based on wording.

# Reply with ONLY ONE WORD: patient OR doctor.

# Message:
# \"\"\"{text}\"\"\"
# """

#     response = model.generate_content(prompt)
#     user_type = response.text.strip().lower()

#     state["user_type"] = user_type if user_type in ("patient", "doctor") else "patient"
#     return state

from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def detect_user_type_node(state: CaseState) -> CaseState:
    if state.get("user_type") in ("patient", "doctor"):
        return state  # Already detected
    model = get_model()
    text = state.get("current_message", "")

    prompt = f"""
You are an expert medical investigator.

Your task is to decide WHO wrote the message:
patient OR doctor.

Think carefully. This is important.

HOW TO DECIDE:

PATIENT:
- Written in first person ("I", "me", "my")
- The sender is describing THEIR OWN symptoms
- Casual or emotional tone
- Example: "I have a headache after taking paracetamol"

DOCTOR:
- Written like medical notes or case summaries
- Neutral, professional, or clinical tone
- Often no "I" or "my"
- Uses medical language, doses, timing, abbreviations
- Sounds like documentation, not a personal chat

IMPORTANT RULES:
- If the message does NOT clearly say "I" or "my", strongly suspect DOCTOR
- If dosage, frequency, dates, or onset are mentioned → DOCTOR
- If the message sounds like something written in a patient record → DOCTOR
- If unsure, choose DOCTOR

Reply with ONLY ONE WORD:
patient OR doctor

Message:
<<<
{text}
>>>
"""

    response = model.generate_content(prompt)
    user_type = response.text.strip().lower()

    state["user_type"] = user_type if user_type in ("patient", "doctor") else "patient"
    return state
