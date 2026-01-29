# backend/app/workflows/verify_doctorno.py
"""
Verify doctor by phone number from MongoDB.
Checks the 'doctors' collection in pv_connect database.

DB Structure (from MongoDB):
{
    "_id": ObjectId,
    "doctor_id": "doc_006",
    "name": "Dr. Deepak Jain",
    "phone_number": "+910982197277",
    "license_number": "MCT 159824",
    "verified": true,
    "specialization": "Pediatrician"
}
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.db.mongo_db import mongodb_service


async def verify_doctor_by_phone(phone_number: str) -> Dict[str, Any]:
    """
    Check if doctor exists in 'doctors' collection by phone number.
    
    Returns:
        {
            "is_verified": bool,      # True if verified=True in DB
            "exists": bool,           # True if doctor found in DB
            "doctor_data": dict or None
        }
    """
    # Query the doctors collection
    doctor = await mongodb_service.db.doctors.find_one(
        {"phone_number": phone_number}
    )
    
    if doctor:
        # Doctor found in DB
        is_verified = doctor.get("verified", False)
        
        return {
            "is_verified": is_verified,
            "exists": True,
            "doctor_data": {
                "doctor_id": doctor.get("doctor_id"),
                "name": doctor.get("name"),
                "phone_number": doctor.get("phone_number"),
                "license_number": doctor.get("license_number"),
                "verified": is_verified,
                "specialization": doctor.get("specialization")
            }
        }
    
    # Doctor not found
    return {
        "is_verified": False,
        "exists": False,
        "doctor_data": None
    }


async def add_doctor_pending_verification(
    phone_number: str,
    license_id: str,
    name: Optional[str] = None
) -> str:
    """
    Add a new doctor to the collection with verified=False.
    Returns the generated doctor_id.
    """
    # Generate doctor_id
    count = await mongodb_service.db.doctors.count_documents({})
    doctor_id = f"doc_{str(count + 1).zfill(4)}"
    
    doctor_doc = {
        "doctor_id": doctor_id,
        "name": name,
        "phone_number": phone_number,
        "license_number": None,  # Will be filled after OCR
        "license_media_id": license_id,
        "verified": False,
        "specialization": None,
        "pending_review": True,
        "created_at": datetime.utcnow()
    }
    
    await mongodb_service.db.doctors.insert_one(doctor_doc)
    return doctor_id


async def mark_doctor_verified(phone_number: str, license_number: str = None) -> bool:
    """
    Mark a doctor as verified after human review.
    """
    update_data = {"verified": True, "pending_review": False}
    if license_number:
        update_data["license_number"] = license_number
    
    result = await mongodb_service.db.doctors.update_one(
        {"phone_number": phone_number},
        {"$set": update_data}
    )
    return result.modified_count > 0


async def get_all_pending_doctors() -> list:
    """
    Get all doctors pending verification (for admin panel).
    """
    cursor = mongodb_service.db.doctors.find({"pending_review": True})
    return await cursor.to_list(length=100)
