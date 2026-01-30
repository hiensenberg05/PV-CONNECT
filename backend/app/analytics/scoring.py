"""
VigiGrade: Confidence Scoring Engine for Pharmacovigilance Cases

This module provides automated data quality assessment for adverse event reports
by calculating completeness scores based on critical field presence and validity.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataQualityGrade(str, Enum):
    """Data quality classification based on completeness score"""
    EXCELLENT = "Excellent"  # 0.90 - 1.00
    HIGH = "High"            # 0.75 - 0.89
    MODERATE = "Moderate"    # 0.60 - 0.74
    LOW = "Low"              # 0.40 - 0.59
    POOR = "Poor"            # 0.00 - 0.39


class VigiGradeScorer:
    """
    Calculates completeness scores for pharmacovigilance case reports.
    
    Scoring Algorithm:
    - Starts with perfect score (1.0)
    - Applies penalties for missing critical fields
    - Returns score (0.0-1.0), grade, and missing field details
    """
    
    # Penalty weights for missing critical fields
    PENALTIES = {
        "reaction_start_date": 0.20,  # Critical for Time-to-Onset analysis
        "medicine_details_empty": 0.15,  # No suspect drug identified
        "medicine_start_date": 0.10,  # Unknown therapy initiation
        "patient_age": 0.10,  # Demographics incomplete
        "patient_gender": 0.05,  # Demographics incomplete
        "severity_empty": 0.10,  # Impact assessment missing
        "description_insufficient": 0.10,  # Inadequate narrative
    }
    
    # Minimum description length for adequate narrative
    MIN_DESCRIPTION_LENGTH = 10
    
    def __init__(self):
        """Initialize the scorer with logging"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _safe_get(self, data: Dict, path: str, default: Any = None) -> Any:
        """
        Safely retrieve nested dictionary values using dot notation.
        
        Args:
            data: Source dictionary
            path: Dot-separated path (e.g., "patient_details.age_value")
            default: Value to return if path doesn't exist
            
        Returns:
            Value at path or default
        """
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, default)
            else:
                return default
        
        return current
    
    def _is_empty_or_unknown(self, value: Any) -> bool:
        """
        Check if a value is considered missing or invalid.
        
        Args:
            value: Value to check
            
        Returns:
            True if value is None, empty string, "Unknown", or empty collection
        """
        if value is None:
            return True
        
        if isinstance(value, str):
            return not value.strip() or value.strip().lower() == "unknown"
        
        if isinstance(value, (list, dict)):
            return len(value) == 0
        
        return False
    
    def _assess_patient_details(self, data: Dict) -> tuple[float, List[str]]:
        """
        Assess patient demographics completeness.
        
        Args:
            data: Case data dictionary
            
        Returns:
            Tuple of (penalty_total, missing_fields_list)
        """
        penalty = 0.0
        missing = []
        
        patient_details = data.get("patient_details", {})
        
        # Check age
        age_value = patient_details.get("age_value")
        if self._is_empty_or_unknown(age_value):
            penalty += self.PENALTIES["patient_age"]
            missing.append("patient_details.age_value")
        
        # Check gender
        gender = patient_details.get("gender")
        if self._is_empty_or_unknown(gender):
            penalty += self.PENALTIES["patient_gender"]
            missing.append("patient_details.gender")
        
        return penalty, missing
    
    def _assess_medicine_details(self, data: Dict) -> tuple[float, List[str]]:
        """
        Assess medicine/drug information completeness.
        
        Args:
            data: Case data dictionary
            
        Returns:
            Tuple of (penalty_total, missing_fields_list)
        """
        penalty = 0.0
        missing = []
        
        medicine_details = data.get("medicine_details", [])
        
        # Check if medicine array is empty
        if not medicine_details or len(medicine_details) == 0:
            penalty += self.PENALTIES["medicine_details_empty"]
            missing.append("medicine_details")
            return penalty, missing
        
        # Check first medicine entry for start date
        first_medicine = medicine_details[0]
        start_date = first_medicine.get("start_date")
        
        if self._is_empty_or_unknown(start_date):
            penalty += self.PENALTIES["medicine_start_date"]
            missing.append("medicine_details[0].start_date")
        
        return penalty, missing
    
    def _assess_reaction_details(self, data: Dict) -> tuple[float, List[str]]:
        """
        Assess adverse reaction information completeness.
        
        Args:
            data: Case data dictionary
            
        Returns:
            Tuple of (penalty_total, missing_fields_list)
        """
        penalty = 0.0
        missing = []
        
        reaction_details = data.get("reaction_details", {})
        start_date = reaction_details.get("start_date")
        
        if self._is_empty_or_unknown(start_date):
            penalty += self.PENALTIES["reaction_start_date"]
            missing.append("reaction_details.start_date")
        
        return penalty, missing
    
    def _assess_severity(self, data: Dict) -> tuple[float, List[str]]:
        """
        Assess severity information completeness.
        
        Args:
            data: Case data dictionary
            
        Returns:
            Tuple of (penalty_total, missing_fields_list)
        """
        penalty = 0.0
        missing = []
        
        severity = data.get("severity", [])
        
        if self._is_empty_or_unknown(severity):
            penalty += self.PENALTIES["severity_empty"]
            missing.append("severity")
        
        return penalty, missing
    
    def _assess_description(self, data: Dict) -> tuple[float, List[str]]:
        """
        Assess case narrative/description completeness.
        
        Args:
            data: Case data dictionary
            
        Returns:
            Tuple of (penalty_total, missing_fields_list)
        """
        penalty = 0.0
        missing = []
        
        description = data.get("description", "")
        
        if isinstance(description, str):
            if len(description.strip()) < self.MIN_DESCRIPTION_LENGTH:
                penalty += self.PENALTIES["description_insufficient"]
                missing.append("description")
        else:
            penalty += self.PENALTIES["description_insufficient"]
            missing.append("description")
        
        return penalty, missing
    
    def _determine_grade(self, score: float) -> str:
        """
        Map numerical score to quality grade.
        
        Args:
            score: Completeness score (0.0 - 1.0)
            
        Returns:
            Quality grade string
        """
        if score >= 0.90:
            return DataQualityGrade.EXCELLENT
        elif score >= 0.75:
            return DataQualityGrade.HIGH
        elif score >= 0.60:
            return DataQualityGrade.MODERATE
        elif score >= 0.40:
            return DataQualityGrade.LOW
        else:
            return DataQualityGrade.POOR
    
    def calculate_score(self, case_data: Dict) -> Dict[str, Any]:
        """
        Calculate completeness score for a case report.
        
        Args:
            case_data: Complete case document with 'data' field
            
        Returns:
            Dictionary containing:
                - score: Float (0.0 - 1.0)
                - grade: Quality classification
                - missing_fields: List of missing critical fields
                - penalty_breakdown: Detailed penalty information
                
        Example:
            >>> scorer = VigiGradeScorer()
            >>> result = scorer.calculate_score(case_doc)
            >>> print(result)
            {
                "score": 0.85,
                "grade": "High",
                "missing_fields": ["patient_details.age_value"],
                "penalty_breakdown": {"patient_age": 0.10}
            }
        """
        try:
            # Extract the 'data' section
            data = case_data.get("data", {})
            
            if not data:
                self.logger.warning(
                    f"Case {case_data.get('case_id', 'UNKNOWN')} has no 'data' field"
                )
                return {
                    "score": 0.0,
                    "grade": DataQualityGrade.POOR,
                    "missing_fields": ["data"],
                    "penalty_breakdown": {}
                }
            
            # Initialize tracking
            total_penalty = 0.0
            all_missing_fields = []
            penalty_breakdown = {}
            
            # Assess each section
            assessments = [
                ("patient", self._assess_patient_details),
                ("medicine", self._assess_medicine_details),
                ("reaction", self._assess_reaction_details),
                ("severity", self._assess_severity),
                ("description", self._assess_description),
            ]
            
            for section_name, assess_func in assessments:
                penalty, missing = assess_func(data)
                total_penalty += penalty
                all_missing_fields.extend(missing)
                
                if penalty > 0:
                    penalty_breakdown[section_name] = round(penalty, 2)
            
            # Calculate final score (ensure non-negative)
            score = max(0.0, 1.0 - total_penalty)
            score = round(score, 2)
            
            # Determine grade
            grade = self._determine_grade(score)
            
            result = {
                "score": score,
                "grade": grade,
                "missing_fields": all_missing_fields,
                "penalty_breakdown": penalty_breakdown
            }
            
            self.logger.info(
                f"Calculated score for case {case_data.get('case_id', 'UNKNOWN')}: "
                f"{score} ({grade})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                f"Error calculating score for case "
                f"{case_data.get('case_id', 'UNKNOWN')}: {str(e)}",
                exc_info=True
            )
            # Return minimal score on error
            return {
                "score": 0.0,
                "grade": DataQualityGrade.POOR,
                "missing_fields": ["error_during_calculation"],
                "penalty_breakdown": {},
                "error": str(e)
            }


async def calculate_score(case_data: Dict) -> Dict[str, Any]:
    """
    Async wrapper for score calculation.
    
    This function provides a simple async interface for the VigiGrade scorer,
    suitable for use in async FastAPI endpoints or background tasks.
    
    Args:
        case_data: Complete case document
        
    Returns:
        Score calculation result dictionary
        
    Example:
        >>> result = await calculate_score(case_document)
        >>> print(f"Score: {result['score']}, Grade: {result['grade']}")
    """
    scorer = VigiGradeScorer()
    return scorer.calculate_score(case_data)


async def update_case_score(case_id: str, db) -> Optional[Dict[str, Any]]:
    """
    Calculate and update the confidence score for a case in MongoDB.
    
    This function:
    1. Fetches the case document by ID
    2. Calculates the completeness score
    3. Updates the document with score and quality report
    
    Args:
        case_id: Unique case identifier
        db: Motor AsyncIOMotorDatabase instance
        
    Returns:
        Updated score result dictionary or None if case not found
        
    Raises:
        Exception: If database operation fails
        
    Example:
        >>> from motor.motor_asyncio import AsyncIOMotorClient
        >>> client = AsyncIOMotorClient("mongodb://localhost:27017")
        >>> db = client.pharmacovigilance
        >>> result = await update_case_score("CASE-001", db)
        >>> print(f"Updated case with score: {result['score']}")
    """
    try:
        logger.info(f"Updating confidence score for case: {case_id}")
        
        # Fetch the case document
        cases_collection = db.cases
        case_doc = await cases_collection.find_one({"case_id": case_id})
        
        if not case_doc:
            logger.warning(f"Case not found: {case_id}")
            return None
        
        # Calculate score
        scorer = VigiGradeScorer()
        score_result = scorer.calculate_score(case_doc)
        
        # Prepare update document
        update_data = {
            "confidence_score": score_result["score"],
            "data_quality_report": {
                "grade": score_result["grade"],
                "missing": score_result["missing_fields"],
                "penalty_breakdown": score_result.get("penalty_breakdown", {}),
                "calculated_at": datetime.utcnow()
            }
        }
        
        # Update in MongoDB
        result = await cases_collection.update_one(
            {"case_id": case_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(
                f"Successfully updated case {case_id} with score "
                f"{score_result['score']} ({score_result['grade']})"
            )
        else:
            logger.warning(
                f"Case {case_id} found but not modified (may already have same score)"
            )
        
        return score_result
        
    except Exception as e:
        logger.error(
            f"Error updating score for case {case_id}: {str(e)}",
            exc_info=True
        )
        raise


async def batch_update_scores(db, case_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Update scores for multiple cases in batch.
    
    Args:
        db: Motor AsyncIOMotorDatabase instance
        case_ids: List of specific case IDs to update, or None for all cases
        
    Returns:
        Summary dictionary with update statistics
        
    Example:
        >>> summary = await batch_update_scores(db, ["CASE-001", "CASE-002"])
        >>> print(f"Updated {summary['successful']} cases")
    """
    logger.info("Starting batch score update")
    
    successful = 0
    failed = 0
    errors = []
    
    try:
        cases_collection = db.cases
        
        # Build query
        query = {}
        if case_ids:
            query["case_id"] = {"$in": case_ids}
        
        # Fetch cases
        cursor = cases_collection.find(query)
        
        async for case_doc in cursor:
            case_id = case_doc.get("case_id", "UNKNOWN")
            
            try:
                await update_case_score(case_id, db)
                successful += 1
            except Exception as e:
                failed += 1
                errors.append({
                    "case_id": case_id,
                    "error": str(e)
                })
                logger.error(f"Failed to update case {case_id}: {str(e)}")
        
        summary = {
            "total_processed": successful + failed,
            "successful": successful,
            "failed": failed,
            "errors": errors
        }
        
        logger.info(
            f"Batch update complete: {successful} successful, {failed} failed"
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Batch update failed: {str(e)}", exc_info=True)
        raise
