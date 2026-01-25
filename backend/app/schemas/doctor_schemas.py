"""
Pydantic schemas for doctor verification and registry
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class DoctorRegistry(BaseModel):
    """Doctor registry entry"""
    
    phone_number: str = Field(..., description="Doctor's registered phone number")
    full_name: str
    license_number: str
    specialty: Optional[str] = None
    institution: Optional[str] = None
    country: str
    
    # Verification status
    verified: bool = Field(default=False)
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = Field(None, description="Admin who verified")
    
    # Metadata
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "full_name": "Dr. Jane Smith",
                "license_number": "MD123456",
                "specialty": "Internal Medicine",
                "institution": "City Hospital",
                "country": "US",
                "verified": True
            }
        }


class LicenseVerification(BaseModel):
    """License verification request"""
    
    phone_number: str
    license_image_url: str = Field(..., description="URL to uploaded license image")
    extracted_info: Optional[dict] = Field(None, description="OCR-extracted information")
    
    # Verification workflow
    status: Literal["pending", "approved", "rejected"] = Field(default="pending")
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # Timestamps
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "license_image_url": "https://cloudinary.com/...",
                "status": "pending",
                "extracted_info": {
                    "name": "Dr. Jane Smith",
                    "license_number": "MD123456"
                }
            }
        }


class DoctorVerificationResponse(BaseModel):
    """Response for doctor verification check"""
    
    is_verified: bool
    registry_entry: Optional[DoctorRegistry] = None
    license_status: Optional[Literal["pending", "approved", "rejected"]] = None
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_verified": True,
                "registry_entry": {
                    "phone_number": "+1234567890",
                    "full_name": "Dr. Jane Smith",
                    "verified": True
                },
                "license_status": "approved",
                "message": "Doctor verified successfully"
            }
        }
