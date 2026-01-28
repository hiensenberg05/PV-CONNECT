# backend/app/schemas/message.py

from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime


class MessageIn(BaseModel):
    """Incoming message from WhatsApp (parsed by Jatin's API layer)"""
    phone_number: str
    message_type: Literal["text", "audio", "document", "image"]
    
    # Content (one of these will be populated based on message_type)
    text_content: Optional[str] = None
    audio_media_id: Optional[str] = None
    document_media_id: Optional[str] = None
    image_media_id: Optional[str] = None
    document_filename: Optional[str] = None
    
    timestamp: datetime
    whatsapp_message_id: str
    
    # Optional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageOut(BaseModel):
    """Outgoing message to send back via WhatsApp"""
    text: str  # Localized reply text
    buttons: Optional[List[str]] = None  # Quick reply buttons (e.g., ["Male", "Female", "Other"])
    requires_input: bool = True  # Does this message expect user input?
    show_file_upload: bool = False  # Show file upload option in UI
    language: Optional[str] = None  # Language of the reply
    
    # Optional: Additional metadata for WhatsApp formatting
    metadata: Dict[str, Any] = Field(default_factory=dict)