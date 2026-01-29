# backend/app/schemas/case.py
"""
Final PvPI case schema stored in MongoDB.
Format matches the required structure for regulatory reporting.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
from uuid import UUID
from datetime import datetime


class PatientDetails(BaseModel):
    """Patient information section."""
    name: Optional[str] = None
    gender: Optional[str] = None
    age_value: Optional[int] = None
    age_unit: Optional[str] = None  # years, months, days


class MedicineDetail(BaseModel):
    """Individual medicine details."""
    name: Optional[str] = None
    quantity_taken: Optional[str] = None
    dosage_form: Optional[str] = None  # tablet, syrup, injection, etc.
    expiry_date: Optional[str] = None
    start_date: Optional[str] = None
    stop_date: Optional[str] = None
    reason_for_medicine: Optional[str] = None
    advised_by: Optional[str] = None
    self_medicated: Optional[bool] = None


class ReactionDetails(BaseModel):
    """Side effect/reaction information."""
    start_date: Optional[str] = None
    continuing: Optional[bool] = None
    stop_date: Optional[str] = None


class CaseData(BaseModel):
    """
    Nested data structure for the case.
    Organizes extracted_data into proper sections.
    """
    patient_details: PatientDetails = Field(default_factory=PatientDetails)
    medicine_details: List[MedicineDetail] = Field(default_factory=list)
    reaction_details: ReactionDetails = Field(default_factory=ReactionDetails)
    severity: List[str] = Field(default_factory=list)  # list of severity types
    description: str = ""
    management_action: Optional[str] = None
    past_disease_history: Optional[str] = None


class Case(BaseModel):
    """
    Final PvPI case stored in MongoDB.
    
    Example:
    {
        "case_id": "uuid",
        "patient_phone": "9198xxxxxxx",
        "reporter_type": "patient | doctor",
        "data": {
            "patient_details": {...},
            "medicine_details": [...],
            "reaction_details": {...},
            "severity": [...],
            "description": ""
        },
        "is_complete": true,
        "created_at": "ISO_DATETIME",
        "updated_at": "ISO_DATETIME"
    }
    """

    case_id: str  # UUID as string
    patient_phone: str
    reporter_type: Literal["patient", "doctor"]

    data: CaseData = Field(default_factory=CaseData)

    is_complete: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat(),
        }

    def to_mongo_doc(self) -> Dict[str, Any]:
        """Convert to MongoDB document format."""
        doc = self.model_dump()
        doc["created_at"] = self.created_at.isoformat()
        doc["updated_at"] = self.updated_at.isoformat()
        return doc
