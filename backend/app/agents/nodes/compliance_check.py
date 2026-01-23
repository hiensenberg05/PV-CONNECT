from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)

# TODO: Replace with real compliance requirements from database
REQUIRED_FIELDS = ["drug_name", "symptoms"]
OPTIONAL_FIELDS = ["severity", "start_date", "dosage"]


def calculate_completeness_score(data: dict, required: list, optional: list) -> float:
    """Calculate completeness score (0.0 to 1.0)"""
    if not required:
        return 1.0
    
    required_count = sum(1 for field in required if data.get(field))
    optional_count = sum(1 for field in optional if data.get(field))
    
    required_score = required_count / len(required) if required else 0
    optional_score = optional_count / len(optional) if optional else 0
    
    # Weight: 70% required, 30% optional
    return (required_score * 0.7) + (optional_score * 0.3)


async def check_compliance_node(state: GraphState) -> GraphState:
    """
    Check if extracted data meets minimum compliance requirements
    RULE-BASED - NO LLM
    """
    extracted_data = state.get("extracted_data", {})
    
    # Check for required fields
    missing = []
    for field in REQUIRED_FIELDS:
        value = extracted_data.get(field)
        # Check if field exists and has non-empty value
        if not value or (isinstance(value, list) and len(value) == 0):
            missing.append(field)
    
    # Calculate completeness score
    completeness_score = calculate_completeness_score(
        extracted_data, 
        REQUIRED_FIELDS, 
        OPTIONAL_FIELDS
    )
    
    # Determine if complete (all required fields present)
    is_complete = len(missing) == 0
    
    state["missing_fields"] = missing
    state["completeness_score"] = completeness_score
    state["is_complete"] = is_complete
    
    logger.info(f"Compliance check: complete={is_complete}, missing={missing}, score={completeness_score:.2f}")
    
    return state
