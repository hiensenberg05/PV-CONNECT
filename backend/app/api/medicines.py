# backend/app/api/medicines.py
"""
API endpoints for fetching medicines from drugs_database collection.
"""

from fastapi import APIRouter, Query
from app.db.mongo_db import mongodb_service
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/medicines", tags=["medicines"])


@router.get("")
async def get_medicines(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    search: Optional[str] = Query(None)
):
    """
    Fetch medicines from the drugs_database collection.
    
    Args:
        limit: Maximum number of medicines to return (default 50)
        skip: Number of medicines to skip for pagination
        search: Optional search query for drug_name or generic_name
    """
    try:
        db = mongodb_service.db
        if db is None:
            return {
                "success": False,
                "error": "Database not connected",
                "data": [],
                "total": 0
            }
        
        collection = db["drugs_database"]
        
        # Build query
        query = {}
        if search:
            query = {
                "$or": [
                    {"drug_name": {"$regex": search, "$options": "i"}},
                    {"generic_name": {"$regex": search, "$options": "i"}}
                ]
            }
        
        # Get total count
        total = await collection.count_documents(query)
        
        # Fetch medicines
        cursor = collection.find(query).skip(skip).limit(limit)
        medicines = []
        
        async for doc in cursor:
            medicines.append({
                "id": str(doc.get("_id")),
                "drug_name": doc.get("drug_name", "Unknown"),
                "generic_name": doc.get("generic_name", "Unknown"),
                "known_side_effects": doc.get("known_side_effects", []),
                "common_dosages": doc.get("common_dosages", []),
                "approved_countries": doc.get("approved_countries", [])
            })
        
        logger.info(f"Fetched {len(medicines)} medicines from drugs_database")
        
        return {
            "success": True,
            "data": medicines,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Error fetching medicines: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "total": 0
        }


@router.get("/count")
async def get_medicines_count():
    """Get total count of medicines in the database."""
    try:
        db = mongodb_service.db
        if db is None:
            return {"success": False, "count": 0, "error": "Database not connected"}
        
        collection = db["drugs_database"]
        count = await collection.count_documents({})
        return {"success": True, "count": count}
    except Exception as e:
        logger.error(f"Error counting medicines: {e}")
        return {"success": False, "count": 0, "error": str(e)}
