from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime


class Case(BaseModel):
    """
    Final PvPI case stored in MongoDB.
    """

    case_id: UUID

    patient_phone: str
    reporter_type: str  # patient / doctor

    data: Dict[str, Any]

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    is_complete: bool = False

    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
        }
