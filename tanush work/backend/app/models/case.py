from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class Case(BaseModel):
    id: str = Field(..., alias="_id")
    phone_number: str
    country: str
    language: str
    user_type: str
    adverse_event: Dict[str, Any] = {}
    documents: List[Dict[str, Any]] = []
    voice_notes: List[Dict[str, Any]] = []
    compliance: Dict[str, Any] = {}
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
