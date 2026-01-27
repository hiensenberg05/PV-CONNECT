"""
Pydantic schemas for pharmacovigilance case data
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ExtractedData(BaseModel):
    """Structured pharmacovigilance data extracted from conversation"""
    
    # Drug Information
    drug_name: Optional[str] = Field(None, description="Brand or generic drug name")
    drug_dosage: Optional[str] = Field(None, description="Dosage amount (e.g., 500mg)")
    drug_frequency: Optional[str] = Field(None, description="Frequency (e.g., BID, TID, once daily)")
    drug_route: Optional[str] = Field(None, description="Route of administration (oral, IV, etc.)")
    
    # Adverse Event Information
    symptoms: Optional[list[str]] = Field(None, description="List of symptoms/adverse events")
    severity: Optional[Literal["mild", "moderate", "severe", "life-threatening"]] = None
    timeline: Optional[str] = Field(None, description="When symptoms started (e.g., '2 days after starting medication')")
    duration: Optional[str] = Field(None, description="How long symptoms lasted")
    
    # Patient Information
    patient_age: Optional[int] = None
    patient_gender: Optional[Literal["male", "female", "other"]] = None
    patient_weight: Optional[str] = None
    
    # Medical Context
    indication: Optional[str] = Field(None, description="Why the drug was prescribed")
    medical_history: Optional[list[str]] = Field(None, description="Relevant medical history")
    concomitant_medications: Optional[list[str]] = Field(None, description="Other medications being taken")
    
    # Outcome
    outcome: Optional[Literal["recovered", "recovering", "not_recovered", "fatal", "unknown"]] = None
    action_taken: Optional[str] = Field(None, description="What action was taken (stopped drug, dose reduced, etc.)")
    
    # Additional Context
    reporter_relationship: Optional[str] = Field(None, description="Relationship to patient (self, parent, doctor, etc.)")
    clinic_name: Optional[str] = None
    prescription_date: Optional[str] = None


class CompletenessCheck(BaseModel):
    """Result of completeness validation"""
    
    completeness_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0 to 1")
    missing_fields: list[str] = Field(default_factory=list, description="List of required fields that are missing")
    is_complete: bool = Field(..., description="Whether all required fields are present")
    recommendations: list[str] = Field(default_factory=list, description="Suggested follow-up questions")


class ConfidenceScore(BaseModel):
    """Confidence scoring for case quality"""
    
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    consistency_score: float = Field(..., ge=0.0, le=1.0, description="Internal consistency of reported data")
    plausibility_score: float = Field(..., ge=0.0, le=1.0, description="Medical plausibility")
    reporter_credibility: float = Field(..., ge=0.0, le=1.0, description="Credibility of reporter")
    data_quality: float = Field(..., ge=0.0, le=1.0, description="Quality and specificity of data")
    flags: list[str] = Field(default_factory=list, description="Any red flags or concerns")


class TriageResult(BaseModel):
    """Clinical triage classification"""
    
    classification: Literal["known", "unusual", "severe"] = Field(..., description="Triage category")
    known_side_effects: list[str] = Field(default_factory=list, description="Known side effects that match")
    unusual_aspects: list[str] = Field(default_factory=list, description="Unusual or unexpected aspects")
    severity_indicators: list[str] = Field(default_factory=list, description="Indicators of severity")
    escalation_required: bool = Field(..., description="Whether case needs escalation")
    reasoning: str = Field(..., description="Explanation of classification")


class CaseDocument(BaseModel):
    """Complete case document for MongoDB storage"""
    
    case_id: str = Field(..., description="Unique case identifier")
    sender_phone: str
    sender_type: Optional[Literal["patient", "doctor"]] = None
    language: str
    country: Optional[str] = None
    
    # Doctor verification (if applicable)
    verified_doctor: bool = False
    license_status: Optional[Literal["pending", "approved", "rejected"]] = None
    
    # Extracted data
    extracted_data: ExtractedData
    
    # Scoring
    completeness_score: float
    confidence_score: float
    
    # Triage
    triage_classification: Optional[Literal["known", "unusual", "severe"]] = None
    triage_result: Optional[TriageResult] = None
    
    # Communication history
    messages: list[dict] = Field(default_factory=list)
    attachments: list[dict] = Field(default_factory=list)
    
    # Status
    status: Literal["open", "escalated", "closed"]
    current_node: Optional[str] = Field(None, description="Current workflow node")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "CASE-2024-001234",
                "sender_phone": "+1234567890",
                "sender_type": "patient",
                "language": "en",
                "extracted_data": {
                    "drug_name": "Aspirin",
                    "drug_dosage": "500mg",
                    "symptoms": ["rash", "itching"],
                    "timeline": "2 hours after taking"
                },
                "completeness_score": 0.8,
                "confidence_score": 0.75,
                "status": "open"
            }
        }
