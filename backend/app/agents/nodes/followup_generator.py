from app.services.gemini_service import generate_followup
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


def prioritize_field(missing_fields: list) -> str:
    """Prioritize which missing field to ask about first"""
    priority_order = ["drug_name", "symptoms", "severity", "start_date", "dosage", "duration"]
    
    for field in priority_order:
        if field in missing_fields:
            return field
    
    # Return first missing field if not in priority list
    return missing_fields[0] if missing_fields else "details"


async def generate_followup_node(state: GraphState) -> GraphState:
    """
    Generate ONE follow-up question for the most critical missing field
    Uses LLM to generate empathetic, simple question
    """
    missing_fields = state.get("missing_fields", [])
    language = state.get("language", "en")
    extracted_data = state.get("extracted_data", {})
    
    if not missing_fields:
        logger.warning("No missing fields but follow-up requested")
        state["next_question"] = "Is there anything else you'd like to add?"
        return state
    
    # Prioritize which field to ask about
    priority_field = prioritize_field(missing_fields)
    
    try:
        question = await generate_followup(priority_field, language, extracted_data)
        state["next_question"] = question
        logger.info(f"Generated follow-up for field: {priority_field}")
    except Exception as e:
        logger.error(f"Follow-up generation error: {e}")
        # Fallback question
        state["next_question"] = f"Can you provide more information about {priority_field}?"
    
    return state
