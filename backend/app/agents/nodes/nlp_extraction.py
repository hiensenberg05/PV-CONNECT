from app.services.gemini_service import extract_adverse_event
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def extract_data_node(state: GraphState) -> GraphState:
    """
    Extract adverse event data from free text using LLM
    MOST CRITICAL NODE - handles partial extraction gracefully
    """
    message = state.get("message", "")
    
    if not message:
        logger.warning("Empty message in NLP extraction")
        state.setdefault("extracted_data", {})
        return state
    
    try:
        # Extract new data
        extracted = await extract_adverse_event(message)
        
        # Merge with existing data (in case of follow-up conversation)
        existing_data = state.get("extracted_data", {})
        
        # Only update non-null values (preserve existing data)
        for key, value in extracted.items():
            if value is not None:
                existing_data[key] = value
        
        state["extracted_data"] = existing_data
        logger.info(f"Extracted data: {list(extracted.keys())}")
        
    except Exception as e:
        logger.error(f"NLP extraction error: {e}")
        state.setdefault("extracted_data", {})
    
    return state
