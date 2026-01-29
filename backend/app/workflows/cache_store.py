# backend/app/workflows/cache_store.py
"""
In-memory cache for conversation state.
Fast retrieval without DB call every turn.
State is synced to MongoDB periodically or on case completion.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.schemas.conversation_state import ConversationState


# In-memory cache: phone_number -> state (as dict)
_state_cache: Dict[str, Dict[str, Any]] = {}


def get_state(phone_number: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve conversation state from cache.
    Returns None if no active conversation.
    """
    return _state_cache.get(phone_number)


def set_state(phone_number: str, state: Dict[str, Any]) -> None:
    """
    Store conversation state in cache.
    Accepts either dict or ConversationState object.
    """
    if isinstance(state, ConversationState):
        state = state.to_dict()
    
    state["last_updated"] = datetime.utcnow()
    _state_cache[phone_number] = state


def delete_state(phone_number: str) -> bool:
    """
    Remove state from cache (e.g., after case completion).
    """
    if phone_number in _state_cache:
        del _state_cache[phone_number]
        return True
    return False


def has_state(phone_number: str) -> bool:
    """
    Check if state exists in cache.
    """
    return phone_number in _state_cache


def get_all_states() -> Dict[str, Dict[str, Any]]:
    """
    Get all cached states (for debugging/admin).
    """
    return _state_cache.copy()


def clear_all_states() -> None:
    """
    Clear all cached states (for testing/reset).
    """
    _state_cache.clear()
