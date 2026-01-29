# backend/app/schemas/conversation_state.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from uuid import UUID
from datetime import datetime


class FieldStatus(BaseModel):
    """Track status of each field in the PvPI form"""
    field_name: str
    asked: bool = False
    answered: bool = False
    value: Optional[Any] = None
    source: Optional[Literal["user_text", "user_voice", "ocr", "prefilled"]] = None
    ask_count: int = 0
    last_asked_at: Optional[datetime] = None


class ConversationState(BaseModel):
    """Main conversation state - tracks everything about the ongoing chat"""
    
    # Core identifiers
    case_id: Optional[UUID] = None
    user_type: Literal["doctor", "patient"]
    phone_number: str
    
    # Current turn data (reset each message)
    current_message: Optional[str] = None
    document_current_uploaded: bool = False
    voice_current_uploaded: bool = False
    current_doc_data: Optional[Dict[str, Any]] = None  # OCR result from Jatin's service
    current_voice_data: Optional[str] = None  # STT result from Jatin's service
    
    # Field tracking (what's asked, what's answered)
    field_status: Dict[str, FieldStatus] = Field(default_factory=dict)
    
    # Accumulated extracted data across conversation
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Auto-derived missing fields
    missing_fields: List[str] = Field(default_factory=list)
    
    # Doctor-specific flags
    doctor_verified: bool = False
    awaiting_license: bool = False
    
    # Workflow control
    workflow_stage: str = "INIT"
    language: str = "en"  # Detected language (en, hi, etc.)
    
    # Question queue (fields to ask next)
    pending_questions: List[str] = Field(default_factory=list)
    
    # Message history (optional, for context)
    message_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    retry_counts: Dict[str, int] = Field(default_factory=dict)  # per field retry count
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }