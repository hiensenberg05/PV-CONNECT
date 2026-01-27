# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# async def triage_case_node(state: CaseState) -> CaseState:
#     """
#     Classifies case urgency and regular vs unusual effects to guide escalation.
#     """
#     model = get_model()
#     drug = state.get("extracted_data", {}).get("drug_name")
#     symptoms = state.get("extracted_data", {}).get("symptoms", [])
#     severity = state.get("extracted_data", {}).get("severity")

#     prompt = f"""
#     Evaluate pharmacovigilance case for triage.
#     Drug: {drug}
#     Symptoms: {symptoms}
#     Severity: {severity}
#     Return JSON: {{"priority": "low|medium|high", "is_unusual": true/false, "reason": ""}}
#     """
#     response = model.generate_content(prompt)
#     state["triage"] = response.text.strip()
#     return state



import json
from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def triage_case_node(state: CaseState) -> CaseState:
    model = get_model()

    extracted = state.get("extracted_data", {})
    drug = extracted.get("drug_name")
    symptoms = extracted.get("symptoms", [])
    severity = extracted.get("severity")

    # ✅ Safe default if info is weak
    if not drug or not symptoms:
        state["triage"] = {
            "priority": "medium",
            "is_unusual": False,
            "reason": "Insufficient information for confident triage."
        }
        return state

    prompt = f"""
You are a pharmacovigilance safety triage system.

Your ONLY task is to classify case urgency.
Be conservative. Patient safety comes first.

STRICT RULES:
- If severity is "severe" → priority MUST be "high"
- If symptoms include serious or life-threatening reactions → priority MUST be "high"
- If reaction is unexpected or rare for the drug → is_unusual = true
- If unsure → choose the HIGHER priority

Drug: {drug}
Symptoms: {symptoms}
Severity: {severity}

Return ONLY valid JSON.
NO extra text.

JSON schema:
{{
  "priority": "low" | "medium" | "high",
  "is_unusual": true | false,
  "reason": string
}}
"""

    response = model.generate_content(prompt)

    try:
        triage = json.loads(response.text)
    except Exception:
        # ✅ Groq-safe fallback
        triage = {
            "priority": "medium",
            "is_unusual": False,
            "reason": "Model output could not be parsed; default applied."
        }

    state["triage"] = triage
    return state
