# backend/app/workflows/asynchronous_licensecheck.py
"""
Asynchronous license verification.
Runs in background while chat continues.
Doctor can still report cases, but case is flagged as "pending_verification".
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.db.mongo_db import mongodb_service


# Track pending verifications
_pending_verifications: Dict[str, Dict[str, Any]] = {}


async def submit_license_for_verification(
    phone_number: str,
    license_id: str,
    license_ocr_text: Optional[str] = None
) -> str:
    """
    Submit a license for async verification.
    Returns a verification_id for tracking.
    
    The actual verification happens in background:
    - Human reviews the license image
    - Or automated OCR check runs
    
    Chat continues regardless.
    """
    verification_id = f"VER-{phone_number}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    verification_record = {
        "verification_id": verification_id,
        "phone_number": phone_number,
        "license_id": license_id,
        "license_ocr_text": license_ocr_text,
        "status": "pending",  # pending | approved | rejected
        "submitted_at": datetime.utcnow(),
        "reviewed_at": None,
        "reviewer": None,
        "notes": None
    }
    
    # Save to DB
    await mongodb_service.db.license_verifications.insert_one(verification_record)
    
    # Track locally
    _pending_verifications[phone_number] = verification_record
    
    return verification_id


async def check_verification_status(phone_number: str) -> Dict[str, Any]:
    """
    Check if a pending verification has been completed.
    Called periodically or on each message to update state.
    """
    # Check DB for latest status
    record = await mongodb_service.db.license_verifications.find_one(
        {"phone_number": phone_number},
        sort=[("submitted_at", -1)]  # Get latest
    )
    
    if not record:
        return {"status": "not_found", "verified": False}
    
    status = record.get("status", "pending")
    
    return {
        "status": status,
        "verified": status == "approved",
        "verification_id": record.get("verification_id"),
        "reviewed_at": record.get("reviewed_at")
    }


async def approve_license(verification_id: str, reviewer: str, notes: str = None) -> bool:
    """
    Admin function to approve a license.
    Called by human reviewer via admin panel.
    """
    result = await mongodb_service.db.license_verifications.update_one(
        {"verification_id": verification_id},
        {
            "$set": {
                "status": "approved",
                "reviewed_at": datetime.utcnow(),
                "reviewer": reviewer,
                "notes": notes
            }
        }
    )
    
    if result.modified_count > 0:
        # Also add to verified_doctors collection
        record = await mongodb_service.db.license_verifications.find_one(
            {"verification_id": verification_id}
        )
        if record:
            await mongodb_service.db.doctors.update_one(
                {"phone_number": record["phone_number"]},
                {
                    "$set": {
                        "verified": True,
                        "pending_review": False,
                        "verified_at": datetime.utcnow(),
                        "verified_by": reviewer
                    }
                }
            )
        return True
    return False


async def reject_license(verification_id: str, reviewer: str, notes: str) -> bool:
    """
    Admin function to reject a license.
    """
    result = await mongodb_service.db.license_verifications.update_one(
        {"verification_id": verification_id},
        {
            "$set": {
                "status": "rejected",
                "reviewed_at": datetime.utcnow(),
                "reviewer": reviewer,
                "notes": notes
            }
        }
    )
    return result.modified_count > 0
