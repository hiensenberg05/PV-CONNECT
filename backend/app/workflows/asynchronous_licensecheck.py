# backend/app/workflows/asynchronous_licensecheck.py
"""
Asynchronous license verification - FIXED VERSION
Runs in background while chat continues.
Doctor can still report cases, but case is flagged as "pending_verification".

FIXES:
1. Removed unused local dict (or optionally converted to cache)
2. Added error handling
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.db.mongo_db import mongodb_service


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
    
    try:
        # Save to DB
        await mongodb_service.db.license_verifications.insert_one(verification_record)
        return verification_id
    except Exception as e:
        print(f"[async_license] Error submitting verification: {str(e)}")
        raise


async def check_verification_status(phone_number: str) -> Dict[str, Any]:
    """
    Check if a pending verification has been completed.
    Called periodically or on each message to update state.
    """
    try:
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
    except Exception as e:
        print(f"[async_license] Error checking status: {str(e)}")
        return {"status": "error", "verified": False}


async def approve_license(verification_id: str, reviewer: str, notes: str = None) -> bool:
    """
    Admin function to approve a license.
    Called by human reviewer via admin panel.
    """
    try:
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
            # Also update verified_doctors collection
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
    except Exception as e:
        print(f"[async_license] Error approving license: {str(e)}")
        return False


async def reject_license(verification_id: str, reviewer: str, notes: str) -> bool:
    """
    Admin function to reject a license.
    """
    try:
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
        
        # Also update doctor record to mark as rejected
        if result.modified_count > 0:
            record = await mongodb_service.db.license_verifications.find_one(
                {"verification_id": verification_id}
            )
            if record:
                await mongodb_service.db.doctors.update_one(
                    {"phone_number": record["phone_number"]},
                    {
                        "$set": {
                            "verified": False,
                            "pending_review": False,
                            "rejected": True,
                            "rejection_reason": notes,
                            "rejected_at": datetime.utcnow()
                        }
                    }
                )
        
        return result.modified_count > 0
    except Exception as e:
        print(f"[async_license] Error rejecting license: {str(e)}")
        return False


async def get_pending_verifications(limit: int = 50) -> list:
    """
    Get all pending license verifications for admin panel.
    """
    try:
        cursor = mongodb_service.db.license_verifications.find(
            {"status": "pending"},
            sort=[("submitted_at", -1)]
        ).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception as e:
        print(f"[async_license] Error fetching pending: {str(e)}")
        return []