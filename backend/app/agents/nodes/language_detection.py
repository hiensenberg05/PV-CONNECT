from app.services.gemini_service import detect_language
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def detect_language_node(state: GraphState) -> GraphState:
    """Detect language from message text using LLM"""
    message = state.get("message", "")
    
    if not message:
        logger.warning("Empty message in language detection")
        state["language"] = "en"
        return state
    
    try:
        result = await detect_language(message)
        language = result.get("language", "en")
        state["language"] = language
        logger.info(f"Detected language: {language}")
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        state["language"] = "en"  # Default to English on failure
    
    return state
