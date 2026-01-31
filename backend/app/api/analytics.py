from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

router = APIRouter()

@router.get("/signals", response_model=List[Dict[str, Any]])
async def get_faers_signals(limit: int = 100, min_ic: float = 0.0):
    """
    Get BCPNN analysis signals derived from FAERS data.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    try:
        query = {"source": "FAERS"}
        if min_ic > 0:
            query["ic"] = {"$gte": min_ic}
            
        cursor = db.analytics_signals.find(query).sort("ic", -1).limit(limit)
        signals = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for s in signals:
            if "_id" in s:
                s["_id"] = str(s["_id"])
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        client.close()

@router.get("/stats")
async def get_faers_stats():
    """
    Get summary statistics for FAERS analysis.
    """
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    try:
        total_signals = await db.analytics_signals.count_documents({"source": "FAERS", "is_signal": True})
        total_pairs = await db.analytics_signals.count_documents({"source": "FAERS"})
        total_cases = await db.faers_cases.count_documents({"data_source": "FAERS"})
        
        # Get top 5 drugs involved in signals
        pipeline = [
            {"$match": {"source": "FAERS", "is_signal": True}},
            {"$group": {"_id": "$drug", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_drugs = await db.analytics_signals.aggregate(pipeline).to_list(length=5)
        
        return {
            "total_analysis_pairs": total_pairs,
            "detected_signals": total_signals,
            "processed_cases": total_cases,
            "top_signal_drugs": top_drugs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        client.close()
