"""
FastAPI Integration for VigiGrade Confidence Scoring

This module provides REST API endpoints for accessing the VigiGrade
scoring functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from .scoring import (
    calculate_score,
    update_case_score,
    batch_update_scores
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/vigigrade", tags=["vigigrade"])


# Pydantic Models
class ScoreResponse(BaseModel):
    """Response model for score calculation"""
    score: float = Field(..., ge=0.0, le=1.0, description="Completeness score (0.0 - 1.0)")
    grade: str = Field(..., description="Quality grade classification")
    missing_fields: List[str] = Field(..., description="List of missing critical fields")
    penalty_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Detailed penalty information by section"
    )


class CaseScoreUpdate(BaseModel):
    """Response model for case score update"""
    case_id: str
    score: float
    grade: str
    updated_at: datetime


class BatchUpdateRequest(BaseModel):
    """Request model for batch score updates"""
    case_ids: Optional[List[str]] = Field(
        None,
        description="Specific case IDs to update. If None, updates all cases."
    )


class BatchUpdateResponse(BaseModel):
    """Response model for batch update operations"""
    total_processed: int
    successful: int
    failed: int
    errors: List[Dict[str, str]] = Field(default_factory=list)


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    service: str
    timestamp: datetime


# Dependency for database connection
async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency to provide database connection.
    Uses the main app's database connection.
    """
    from ..db.mongo_db import mongodb_service
    return mongodb_service.db


# API Endpoints

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint for VigiGrade service.
    
    Returns service status and current timestamp.
    """
    return HealthCheckResponse(
        status="healthy",
        service="VigiGrade Confidence Scoring Engine",
        timestamp=datetime.utcnow()
    )


@router.post("/calculate", response_model=ScoreResponse)
async def calculate_case_score(
    case_data: Dict[str, Any]
):
    """
    Calculate confidence score for a case without updating the database.
    
    This endpoint accepts a case document and returns the calculated score
    without persisting it to the database. Useful for previewing scores
    or validating data before submission.
    
    Args:
        case_data: Complete case document with 'data' field
        
    Returns:
        Score calculation result
        
    Example Request:
        ```json
        {
            "case_id": "CASE-001",
            "data": {
                "patient_details": {
                    "gender": "Male",
                    "age_value": 25
                },
                "medicine_details": [...],
                "reaction_details": {...},
                "severity": [...],
                "description": "..."
            }
        }
        ```
    """
    try:
        result = await calculate_score(case_data)
        
        return ScoreResponse(
            score=result["score"],
            grade=result["grade"],
            missing_fields=result["missing_fields"],
            penalty_breakdown=result.get("penalty_breakdown", {})
        )
        
    except Exception as e:
        logger.error(f"Error calculating score: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate score: {str(e)}"
        )


@router.post("/cases/{case_id}/update-score", response_model=CaseScoreUpdate)
async def update_score_for_case(
    case_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Calculate and update the confidence score for a specific case.
    
    This endpoint fetches the case from the database, calculates its
    confidence score, and updates the document with the results.
    
    Args:
        case_id: Unique case identifier
        db: Database connection (injected)
        
    Returns:
        Updated score information
        
    Raises:
        404: Case not found
        500: Update failed
    """
    try:
        result = await update_case_score(case_id, db)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Case not found: {case_id}"
            )
        
        return CaseScoreUpdate(
            case_id=case_id,
            score=result["score"],
            grade=result["grade"],
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating score for case {case_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update score: {str(e)}"
        )


@router.get("/cases/{case_id}/score", response_model=ScoreResponse)
async def get_case_score(
    case_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Retrieve the current confidence score for a case.
    
    This endpoint returns the stored confidence score from the database
    without recalculating it.
    
    Args:
        case_id: Unique case identifier
        db: Database connection (injected)
        
    Returns:
        Current score information
        
    Raises:
        404: Case not found or no score available
    """
    try:
        cases_collection = db.cases
        case_doc = await cases_collection.find_one({"case_id": case_id})
        
        if not case_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Case not found: {case_id}"
            )
        
        if "confidence_score" not in case_doc:
            raise HTTPException(
                status_code=404,
                detail=f"No confidence score available for case: {case_id}"
            )
        
        quality_report = case_doc.get("data_quality_report", {})
        
        return ScoreResponse(
            score=case_doc["confidence_score"],
            grade=quality_report.get("grade", "Unknown"),
            missing_fields=quality_report.get("missing", []),
            penalty_breakdown=quality_report.get("penalty_breakdown", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving score for case {case_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve score: {str(e)}"
        )


@router.post("/batch-update", response_model=BatchUpdateResponse)
async def batch_update_case_scores(
    request: BatchUpdateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update confidence scores for multiple cases in batch.
    
    This endpoint can update all cases or a specific list of cases.
    For large batches, the operation runs in the background.
    
    Args:
        request: Batch update request with optional case ID list
        background_tasks: FastAPI background tasks (injected)
        db: Database connection (injected)
        
    Returns:
        Update summary with statistics
        
    Note:
        For batches with >100 cases, processing happens in the background
        and the endpoint returns immediately with initial status.
    """
    try:
        case_ids = request.case_ids
        
        # For small batches, process synchronously
        if case_ids and len(case_ids) <= 100:
            summary = await batch_update_scores(db, case_ids)
            
            return BatchUpdateResponse(
                total_processed=summary["total_processed"],
                successful=summary["successful"],
                failed=summary["failed"],
                errors=summary["errors"]
            )
        
        # For large batches or all cases, process in background
        else:
            background_tasks.add_task(
                batch_update_scores,
                db,
                case_ids
            )
            
            return BatchUpdateResponse(
                total_processed=0,
                successful=0,
                failed=0,
                errors=[{
                    "message": "Batch update started in background. "
                               "Check logs for completion status."
                }]
            )
        
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process batch update: {str(e)}"
        )


@router.get("/statistics")
async def get_score_statistics(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get aggregate statistics about confidence scores across all cases.
    
    Returns distribution of scores by grade, average scores, and other
    useful metrics.
    
    Returns:
        Dictionary with score statistics
    """
    try:
        cases_collection = db.cases
        
        # Aggregate statistics
        pipeline = [
            {
                "$match": {
                    "confidence_score": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": "$data_quality_report.grade",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$confidence_score"},
                    "min_score": {"$min": "$confidence_score"},
                    "max_score": {"$max": "$confidence_score"}
                }
            }
        ]
        
        results = await cases_collection.aggregate(pipeline).to_list(length=None)
        
        # Calculate overall statistics
        total_cases = sum(r["count"] for r in results)
        overall_avg = sum(r["avg_score"] * r["count"] for r in results) / total_cases if total_cases > 0 else 0
        
        return {
            "total_cases_scored": total_cases,
            "overall_average_score": round(overall_avg, 2),
            "distribution_by_grade": {
                r["_id"]: {
                    "count": r["count"],
                    "percentage": round(r["count"] / total_cases * 100, 1) if total_cases > 0 else 0,
                    "avg_score": round(r["avg_score"], 2),
                    "score_range": {
                        "min": round(r["min_score"], 2),
                        "max": round(r["max_score"], 2)
                    }
                }
                for r in results
            },
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate statistics: {str(e)}"
        )


# Example integration with main FastAPI app:
"""
from fastapi import FastAPI
from app.api.vigigrade import router as vigigrade_router

app = FastAPI(title="Pharmacovigilance System")

# Include VigiGrade router
app.include_router(vigigrade_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
