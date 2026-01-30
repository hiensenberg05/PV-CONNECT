# backend/app/schemas/pv_models.py
"""
Pharmacovigilance models for signal detection and analytics.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DrugEventPair(BaseModel):
    """Drug-event pair for signal detection"""
    drug_name: str
    event_term: str
    meddra_code: Optional[str] = None
    count: int = 0
    
    # Disproportionality metrics
    prr: Optional[float] = None  # Proportional Reporting Ratio
    prr_ci_lower: Optional[float] = None
    prr_ci_upper: Optional[float] = None
    
    ror: Optional[float] = None  # Reporting Odds Ratio
    ror_ci_lower: Optional[float] = None
    ror_ci_upper: Optional[float] = None
    
    ic: Optional[float] = None  # Information Component (BCPNN)
    ic_ci_lower: Optional[float] = None
    ic_ci_upper: Optional[float] = None
    
    # Signal status
    is_signal: bool = False
    signal_detected_date: Optional[datetime] = None
    signal_status: Optional[str] = None  # New, Under Review, Confirmed, Refuted
    
    # Metadata
    last_calculated: datetime = Field(default_factory=datetime.utcnow)


class CaseReport(BaseModel):
    """Case report model for signal detection"""
    case_id: str
    received_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Patient info
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None
    
    # Products
    suspect_products: List[dict] = Field(default_factory=list)
    
    # Events
    adverse_events: List[dict] = Field(default_factory=list)
    
    # Status
    status: str = "Pending"
