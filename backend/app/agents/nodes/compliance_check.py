from app.services.mongodb_service import get_db
from app.agents.state import CaseState


async def check_compliance_node(state: CaseState) -> CaseState:
    db = get_db()
    template = db.compliance_templates.find_one({"country": state.get("country", "IN")})
    mandatory = template["mandatory_fields"] if template else []
    extracted = state.get("extracted_data", {})
    missing = [f for f in mandatory if not extracted.get(f)]
    completeness = (len(mandatory) - len(missing)) / len(mandatory) if mandatory else 0

    state["missing_fields"] = missing
    state["completeness_score"] = completeness
    state["requires_followup"] = completeness < 0.7 if mandatory else True
    return state
