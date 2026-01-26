from app.services.ollama_service import triage_case
from app.services.mongodb_service import search_drugs
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def triage_case_node(state: GraphState) -> GraphState:
    """
    Clinical triage - categorize risk level using LLM-assisted analysis
    NOT diagnosis - only risk categorization
    """
    extracted_data = state.get("extracted_data", {})
    drug_name = extracted_data.get("drug_name")
    
    # Fetch known side effects from database (if available)
    known_effects = None
    if drug_name:
        drug_profile = await search_drugs(drug_name)
        if drug_profile:
            known_effects = {
                "known_side_effects": drug_profile.get("known_side_effects", []),
                "drug_name": drug_profile.get("drug_name"),
                "approved_countries": drug_profile.get("approved_countries", [])
            }
            logger.info(f"Found existing drug profile for {drug_name}")
        else:
            logger.warning(f"No drug profile found for {drug_name}")
    
    try:
        triage_result = await triage_case(extracted_data, known_effects)
        
        state["risk_level"] = triage_result.get("risk_level", "medium")
        state["triage_reason"] = triage_result.get("reason", "No reason provided")
        state["requires_human_review"] = triage_result.get("requires_human_review", False)
        
        logger.info(f"Triage result: risk={state['risk_level']}, review={state['requires_human_review']}")
        
    except Exception as e:
        logger.error(f"Triage error: {e}")
        # Default to medium risk on error
        state["risk_level"] = "medium"
        state["triage_reason"] = "Error in triage analysis"
        state["requires_human_review"] = True
    
    return state
