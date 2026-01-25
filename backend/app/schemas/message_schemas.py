"""
Pydantic schemas for message handling
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class MessageInput(BaseModel):
    """Incoming message from user"""
    
    message: Optional[str] = Field("", description="User's message text")
    sender_phone: str = Field(..., description="User's phone number")
    case_id: Optional[str] = Field(None, description="Existing case ID for continuation")
    attachments: Optional[list[dict]] = Field(None, description="List of attachments (images, documents)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I took aspirin and got a rash",
                "sender_phone": "+1234567890",
                "case_id": None,
                "attachments": []
            }
        }


class MessageOutput(BaseModel):
    """Response to user"""
    
    response: str = Field(..., description="Assistant's response message")
    case_id: Optional[str] = Field(None, description="Case ID for this conversation")
    next_action: Optional[str] = Field(None, description="What the user should do next")
    status: Literal["open", "escalated", "closed", "pending_doctor_review"] = Field(..., description="Current case status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Thank you for reporting. Can you tell me when you started experiencing the rash?",
                "case_id": "CASE-2024-001234",
                "next_action": "provide_timeline",
                "status": "open"
            }
        }


class StateResponse(BaseModel):
    """Full state response for debugging/testing"""
    
    case_id: str
    sender_type: Optional[Literal["patient", "doctor"]]
    language: Optional[str]
    extracted_data: dict
    completeness_score: float
    confidence_score: float
    status: Literal["open", "escalated", "closed", "pending_doctor_review"]
    messages: list[dict]
    current_node: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "CASE-2024-001234",
                "sender_type": "patient",
                "language": "en",
                "extracted_data": {
                    "drug_name": "Aspirin",
                    "symptoms": ["rash"]
                },
                "completeness_score": 0.5,
                "confidence_score": 0.6,
                "status": "open",
                "messages": [],
                "current_node": "patient_intake"
            }
        }


class TestScenario(BaseModel):
    """Test scenario for workflow testing"""
    
    scenario_type: Literal["patient", "doctor"]
    messages: list[str] = Field(..., description="Sequence of messages to simulate")
    expected_outcome: Optional[dict] = Field(None, description="Expected final state")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_type": "patient",
                "messages": [
                    "I took aspirin and got a rash",
                    "It started 2 hours after taking the medicine",
                    "500mg tablet"
                ],
                "expected_outcome": {
                    "completeness_score": 0.8,
                    "triage_classification": "known"
                }
            }
        }
