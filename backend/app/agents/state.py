from typing import TypedDict, List, Optional, Dict, Any


class CaseState(TypedDict, total=False):
    case_id: str
    phone_number: str
    country: str
    language: str
    user_type: str
    messages: List[Dict[str, Any]]
    current_message: str
    extracted_data: Dict[str, Any]
    missing_fields: List[str]
    documents: List[Dict[str, Any]]
    voice_notes: List[Dict[str, Any]]
    completeness_score: float
    confidence_score: float
    requires_followup: bool
    next_question: Optional[str]
    response_sent: bool
    doctor_verified: bool
    awaiting_license: bool
