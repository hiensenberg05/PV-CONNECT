from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def triage_case_node(state: CaseState) -> CaseState:
    """
    Classifies case urgency and regular vs unusual effects to guide escalation.
    """
    model = get_model("gemini-2.0-flash-thinking-exp-01-21")
    drug = state.get("extracted_data", {}).get("drug_name")
    symptoms = state.get("extracted_data", {}).get("symptoms", [])
    severity = state.get("extracted_data", {}).get("severity")

    prompt = f"""
    Evaluate pharmacovigilance case for triage.
    Drug: {drug}
    Symptoms: {symptoms}
    Severity: {severity}
    Return JSON: {{"priority": "low|medium|high", "is_unusual": true/false, "reason": ""}}
    """
    response = model.generate_content(prompt)
    state["triage"] = response.text.strip()
    return state
