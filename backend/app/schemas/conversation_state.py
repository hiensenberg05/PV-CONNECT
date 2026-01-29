# backend/app/schemas/conversation_state.py
"""
Conversation state schema - aligned with pv_followup_agent requirements.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from uuid import UUID
from datetime import datetime


# Default extracted_data structure (all fields null initially)
DEFAULT_EXTRACTED_DATA = {
    "patient_name": None,
    "patient_gender": None,
    "patient_age_value": None,
    "patient_age_unit": None,

    "reason_for_medicine": None,
    "medicine_advised_by": None,
    "self_medicated": None,
    "past_disease_history": None,

    "medicine_name": None,
    "medicine_quantity_taken": None,
    "medicine_dosage_form": None,
    "medicine_expiry_date": None,
    "medicine_start_date": None,
    "medicine_stop_date": None,

    "side_effect_start_date": None,
    "side_effect_continuing": None,
    "side_effect_stop_date": None,

    "severity_no_daily_activity_effect": False,
    "severity_affected_daily_activity": False,
    "severity_hospitalized": False,
    "severity_death": False,
    "severity_other": None,

    "side_effect_description": None,
    "management_action_taken": None
}

# Default missing list (all keys that need to be collected)
DEFAULT_MISSING = [
    "patient_name",
    "patient_gender",
    "patient_age_value",
    "patient_age_unit",

    "reason_for_medicine",
    "medicine_advised_by",
    "self_medicated",
    "past_disease_history",

    "medicine_name",
    "medicine_quantity_taken",
    "medicine_dosage_form",
    "medicine_expiry_date",
    "medicine_start_date",
    "medicine_stop_date",

    "side_effect_start_date",
    "side_effect_continuing",
    "side_effect_stop_date",

    "severity_no_daily_activity_effect",
    "severity_affected_daily_activity",
    "severity_hospitalized",
    "severity_death",
    "severity_other",

    "side_effect_description",
    "management_action_taken"
]


class ConversationState(BaseModel):
    """
    Main conversation state - aligned with pv_followup_agent.
    Uses dict keys that agent expects.
    """

    # Core identifiers
    case_id: Optional[str] = None
    phone_number: str
    user_type: Optional[Literal["doctor", "patient"]] = None
    workflow_stage: str = "INIT"  # INIT | ASK_USER_TYPE | COLLECTING | COMPLETE

    # Doctor verification flags
    verified_doctor: Optional[bool] = None  # None for patient, False/True for doctor
    human_verified: Optional[bool] = None   # True if human reviewed license
    license_id: Optional[str] = None
    verification_id: Optional[str] = None

    # Per-turn data (reset each message) - matches agent keys
    current_message: Optional[str] = None
    doc_id: Optional[str] = None
    voice_id: Optional[str] = None
    current_doc_data: Dict[str, Any] = Field(default_factory=dict)  # {"raw_text": "..."}
    current_voice_data: Dict[str, Any] = Field(default_factory=dict)  # {"transcript": "..."}
    problems: List[str] = Field(default_factory=list)
    to_use: str = ""

    # Accumulated data - matches agent keys
    extracted_data: Dict[str, Any] = Field(default_factory=lambda: DEFAULT_EXTRACTED_DATA.copy())
    missing: List[str] = Field(default_factory=lambda: DEFAULT_MISSING.copy())
    chat_history: List[Dict[str, Any]] = Field(default_factory=list)
    doc_all: List[str] = Field(default_factory=list)
    voice_all: List[str] = Field(default_factory=list)

    # Flow control
    case_complete: bool = False
    language: str = "en"
    followup_msg: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for agent consumption."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationState":
        """Create from dict (e.g., from MongoDB)."""
        return cls(**data)