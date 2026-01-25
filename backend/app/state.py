"""
State definition for NOVA LangGraph workflow
"""

from typing import TypedDict, Optional, Literal, List, Dict
from datetime import datetime


class NovaState(TypedDict, total=False):
    """
    Global state for NOVA pharmacovigilance workflow.
    """

    # Case Identification
    case_id: Optional[str]
    sender_phone: Optional[str]

    # User Classification
    sender_type: Optional[Literal["patient", "doctor"]]
    language: Optional[str]
    country: Optional[str]

    # Doctor Verification
    verified_doctor: bool
    license_status: Optional[Literal["pending", "approved", "rejected"]]

    # Extracted Pharmacovigilance Data
    extracted_data: Dict
    missing_fields: List[str]

    # Scoring
    completeness_score: float
    confidence_score: float

    # Communication History
    messages: List[Dict]
    attachments: List[Dict]

    # Case Status
    status: Literal["open", "escalated", "closed", "pending_doctor_review"]

    # Triage
    triage_classification: Optional[Literal["known", "unusual", "severe"]]

    # Metadata
    created_at: Optional[str]
    updated_at: Optional[str]

    # Transient image processing
    pending_image_data: Optional[bytes]
    pending_image_url: Optional[str]
    pending_image_mime_type: Optional[str]

    # Workflow control
    current_node: Optional[str]
    next_action: Optional[str]


def create_initial_state(sender_phone: str, initial_message: str) -> NovaState:
    timestamp = datetime.utcnow().isoformat()

    return NovaState(
        case_id=None,
        sender_phone=sender_phone,
        sender_type=None,
        language=None,
        country=None,
        verified_doctor=False,
        license_status=None,
        extracted_data={},
        missing_fields=[],
        completeness_score=0.0,
        confidence_score=0.0,
        messages=[{
            "role": "user",
            "content": initial_message,
            "timestamp": timestamp
        }],
        attachments=[],
        status="open",
        triage_classification=None,
        created_at=timestamp,
        updated_at=timestamp,
        current_node="initial_classification",
        next_action=None
    )


def update_state_timestamp(state: NovaState) -> NovaState:
    state["updated_at"] = datetime.utcnow().isoformat()
    return state


def add_message_to_state(
    state: NovaState,
    role: Literal["user", "assistant", "system"],
    content: str
) -> NovaState:
    state["messages"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    })
    return update_state_timestamp(state)


def should_skip_classification(state: NovaState) -> bool:
    return state.get("language") is not None and state.get("sender_type") is not None
