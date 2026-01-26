from typing import TypedDict, List, Optional, Dict, Any


class GraphState(TypedDict, total=False):
    """State schema for LangGraph workflow"""
    # Input
    message: str
    from_number: str
    message_type: str  # "text", "image", "audio"
    media_url: Optional[str]
    
    # Detection
    language: str
    user_type: str  # "patient" or "doctor"
    
    # Extraction
    extracted_data: Dict[str, Any]
    has_image: bool
    has_voice: bool
    
    # Compliance
    is_complete: bool
    missing_fields: List[str]
    completeness_score: float
    
    # Triage
    risk_level: str
    triage_reason: str
    requires_human_review: bool
    
    # Follow-up
    next_question: Optional[str]
    
    # Case Management
    case_id: Optional[str]
    confidence_score: float
    
    # Response
    response_sent: bool
    response_message: Optional[str]  # Added for frontend testing


# Alias for backward compatibility
CaseState = GraphState

