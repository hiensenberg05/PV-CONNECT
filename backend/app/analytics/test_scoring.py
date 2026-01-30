"""
Unit tests for VigiGrade Confidence Scoring Engine
"""

import pytest
from datetime import datetime
from app.services.scoring import (
    VigiGradeScorer,
    DataQualityGrade,
    calculate_score,
    update_case_score,
    batch_update_scores
)


class TestVigiGradeScorer:
    """Test suite for VigiGradeScorer class"""
    
    @pytest.fixture
    def scorer(self):
        """Fixture to provide a scorer instance"""
        return VigiGradeScorer()
    
    @pytest.fixture
    def perfect_case(self):
        """Fixture for a case with all required fields"""
        return {
            "_id": "507f1f77bcf86cd799439011",
            "case_id": "CASE-PERFECT-001",
            "data": {
                "patient_details": {
                    "name": "Rahul",
                    "gender": "Male",
                    "age_value": 25,
                    "age_unit": "years"
                },
                "medicine_details": [
                    {
                        "name": "Paracetamol",
                        "quantity_taken": "500mg",
                        "start_date": "2024-01-15"
                    }
                ],
                "reaction_details": {
                    "start_date": "2024-01-16",
                    "continuing": True
                },
                "severity": ["Hospitalized"],
                "description": "Patient developed severe allergic reaction requiring hospitalization."
            }
        }
    
    @pytest.fixture
    def minimal_case(self):
        """Fixture for a case with minimal/missing fields"""
        return {
            "_id": "507f1f77bcf86cd799439012",
            "case_id": "CASE-MINIMAL-001",
            "data": {
                "patient_details": {},
                "medicine_details": [],
                "reaction_details": {},
                "severity": [],
                "description": ""
            }
        }
    
    def test_perfect_case_score(self, scorer, perfect_case):
        """Test that a perfect case receives score of 1.0"""
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 1.0
        assert result["grade"] == DataQualityGrade.EXCELLENT
        assert len(result["missing_fields"]) == 0
        assert len(result["penalty_breakdown"]) == 0
    
    def test_minimal_case_score(self, scorer, minimal_case):
        """Test that a minimal case receives appropriate penalties"""
        result = scorer.calculate_score(minimal_case)
        
        # Expected penalties:
        # - reaction_start_date: 0.20
        # - medicine_details_empty: 0.15
        # - patient_age: 0.10
        # - patient_gender: 0.05
        # - severity_empty: 0.10
        # - description_insufficient: 0.10
        # Total: 0.70
        
        expected_score = 1.0 - 0.70
        assert result["score"] == expected_score
        assert result["grade"] == DataQualityGrade.MODERATE
        assert len(result["missing_fields"]) > 0
    
    def test_missing_reaction_start_date(self, scorer, perfect_case):
        """Test penalty for missing reaction start date (0.20)"""
        perfect_case["data"]["reaction_details"] = {}
        
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 0.80
        assert "reaction_details.start_date" in result["missing_fields"]
        assert "reaction" in result["penalty_breakdown"]
    
    def test_empty_medicine_details(self, scorer, perfect_case):
        """Test penalty for empty medicine array (0.15)"""
        perfect_case["data"]["medicine_details"] = []
        
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 0.85
        assert "medicine_details" in result["missing_fields"]
        assert "medicine" in result["penalty_breakdown"]
    
    def test_missing_medicine_start_date(self, scorer, perfect_case):
        """Test penalty for missing medicine start date (0.10)"""
        perfect_case["data"]["medicine_details"][0]["start_date"] = None
        
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 0.90
        assert "medicine_details[0].start_date" in result["missing_fields"]
    
    def test_missing_patient_age(self, scorer, perfect_case):
        """Test penalty for missing patient age (0.10)"""
        del perfect_case["data"]["patient_details"]["age_value"]
        
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 0.90
        assert "patient_details.age_value" in result["missing_fields"]
    
    def test_missing_patient_gender(self, scorer, perfect_case):
        """Test penalty for missing patient gender (0.05)"""
        perfect_case["data"]["patient_details"]["gender"] = None
        
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 0.95
        assert "patient_details.gender" in result["missing_fields"]
    
    def test_empty_severity(self, scorer, perfect_case):
        """Test penalty for empty severity list (0.10)"""
        perfect_case["data"]["severity"] = []
        
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 0.90
        assert "severity" in result["missing_fields"]
    
    def test_insufficient_description(self, scorer, perfect_case):
        """Test penalty for short description (0.10)"""
        perfect_case["data"]["description"] = "Short"
        
        result = scorer.calculate_score(perfect_case)
        
        assert result["score"] == 0.90
        assert "description" in result["missing_fields"]
    
    def test_unknown_values_treated_as_missing(self, scorer, perfect_case):
        """Test that 'Unknown' string values are treated as missing"""
        perfect_case["data"]["patient_details"]["gender"] = "Unknown"
        perfect_case["data"]["reaction_details"]["start_date"] = "Unknown"
        
        result = scorer.calculate_score(perfect_case)
        
        # Should have penalties for both gender (0.05) and reaction date (0.20)
        assert result["score"] == 0.75
        assert "patient_details.gender" in result["missing_fields"]
        assert "reaction_details.start_date" in result["missing_fields"]
    
    def test_missing_data_section(self, scorer):
        """Test handling of completely missing 'data' section"""
        case = {
            "case_id": "CASE-NO-DATA",
            "_id": "507f1f77bcf86cd799439013"
        }
        
        result = scorer.calculate_score(case)
        
        assert result["score"] == 0.0
        assert result["grade"] == DataQualityGrade.POOR
        assert "data" in result["missing_fields"]
    
    def test_grade_classification_excellent(self, scorer, perfect_case):
        """Test EXCELLENT grade for scores >= 0.90"""
        result = scorer.calculate_score(perfect_case)
        assert result["grade"] == DataQualityGrade.EXCELLENT
    
    def test_grade_classification_high(self, scorer, perfect_case):
        """Test HIGH grade for scores 0.75-0.89"""
        perfect_case["data"]["description"] = "Short"  # -0.10
        perfect_case["data"]["severity"] = []  # -0.10
        
        result = scorer.calculate_score(perfect_case)
        assert result["score"] == 0.80
        assert result["grade"] == DataQualityGrade.HIGH
    
    def test_grade_classification_moderate(self, scorer, perfect_case):
        """Test MODERATE grade for scores 0.60-0.74"""
        perfect_case["data"]["reaction_details"] = {}  # -0.20
        perfect_case["data"]["description"] = "Short"  # -0.10
        perfect_case["data"]["severity"] = []  # -0.10
        
        result = scorer.calculate_score(perfect_case)
        assert result["score"] == 0.60
        assert result["grade"] == DataQualityGrade.MODERATE
    
    def test_grade_classification_low(self, scorer, perfect_case):
        """Test LOW grade for scores 0.40-0.59"""
        perfect_case["data"]["reaction_details"] = {}  # -0.20
        perfect_case["data"]["medicine_details"] = []  # -0.15
        perfect_case["data"]["patient_details"]["age_value"] = None  # -0.10
        perfect_case["data"]["severity"] = []  # -0.10
        
        result = scorer.calculate_score(perfect_case)
        assert result["score"] == 0.45
        assert result["grade"] == DataQualityGrade.LOW
    
    def test_grade_classification_poor(self, scorer, minimal_case):
        """Test POOR grade for scores < 0.40"""
        result = scorer.calculate_score(minimal_case)
        assert result["score"] < 0.40
        assert result["grade"] == DataQualityGrade.POOR
    
    def test_score_never_negative(self, scorer):
        """Test that score cannot go below 0.0"""
        case = {
            "case_id": "CASE-WORST",
            "data": {}
        }
        
        result = scorer.calculate_score(case)
        assert result["score"] >= 0.0
    
    def test_whitespace_only_treated_as_empty(self, scorer, perfect_case):
        """Test that whitespace-only strings are treated as empty"""
        perfect_case["data"]["patient_details"]["gender"] = "   "
        perfect_case["data"]["description"] = "     "
        
        result = scorer.calculate_score(perfect_case)
        
        assert "patient_details.gender" in result["missing_fields"]
        assert "description" in result["missing_fields"]
    
    def test_case_insensitive_unknown(self, scorer, perfect_case):
        """Test that 'unknown' is case-insensitive"""
        perfect_case["data"]["patient_details"]["gender"] = "UNKNOWN"
        
        result = scorer.calculate_score(perfect_case)
        
        assert "patient_details.gender" in result["missing_fields"]
    
    def test_penalty_breakdown_structure(self, scorer, minimal_case):
        """Test that penalty breakdown has expected structure"""
        result = scorer.calculate_score(minimal_case)
        
        assert isinstance(result["penalty_breakdown"], dict)
        for section, penalty in result["penalty_breakdown"].items():
            assert isinstance(section, str)
            assert isinstance(penalty, (int, float))
            assert penalty > 0


class TestAsyncFunctions:
    """Test suite for async wrapper functions"""
    
    @pytest.mark.asyncio
    async def test_calculate_score_async(self):
        """Test async calculate_score wrapper"""
        case_data = {
            "case_id": "CASE-ASYNC-001",
            "data": {
                "patient_details": {
                    "name": "Test",
                    "gender": "Male",
                    "age_value": 30,
                    "age_unit": "years"
                },
                "medicine_details": [
                    {
                        "name": "TestDrug",
                        "start_date": "2024-01-01"
                    }
                ],
                "reaction_details": {
                    "start_date": "2024-01-02"
                },
                "severity": ["Mild"],
                "description": "Test description for async function."
            }
        }
        
        result = await calculate_score(case_data)
        
        assert "score" in result
        assert "grade" in result
        assert "missing_fields" in result
        assert result["score"] == 1.0


@pytest.mark.asyncio
class TestMongoDBIntegration:
    """Test suite for MongoDB integration functions"""
    
    @pytest.fixture
    async def mock_db(self, mocker):
        """Fixture to provide a mocked MongoDB database"""
        mock_db = mocker.MagicMock()
        mock_collection = mocker.MagicMock()
        mock_db.cases = mock_collection
        return mock_db
    
    async def test_update_case_score_success(self, mock_db, mocker):
        """Test successful case score update"""
        # Mock find_one to return a case
        case_doc = {
            "_id": "507f1f77bcf86cd799439011",
            "case_id": "CASE-UPDATE-001",
            "data": {
                "patient_details": {
                    "gender": "Male",
                    "age_value": 25
                },
                "medicine_details": [
                    {
                        "name": "TestDrug",
                        "start_date": "2024-01-01"
                    }
                ],
                "reaction_details": {
                    "start_date": "2024-01-02"
                },
                "severity": ["Mild"],
                "description": "Test description for update."
            }
        }
        
        mock_db.cases.find_one = mocker.AsyncMock(return_value=case_doc)
        
        # Mock update_one
        mock_update_result = mocker.MagicMock()
        mock_update_result.modified_count = 1
        mock_db.cases.update_one = mocker.AsyncMock(return_value=mock_update_result)
        
        # Execute
        result = await update_case_score("CASE-UPDATE-001", mock_db)
        
        # Verify
        assert result is not None
        assert "score" in result
        assert result["score"] == 1.0
        
        # Verify find_one was called
        mock_db.cases.find_one.assert_called_once_with(
            {"case_id": "CASE-UPDATE-001"}
        )
        
        # Verify update_one was called
        assert mock_db.cases.update_one.called
    
    async def test_update_case_score_not_found(self, mock_db, mocker):
        """Test update when case is not found"""
        mock_db.cases.find_one = mocker.AsyncMock(return_value=None)
        
        result = await update_case_score("CASE-NONEXISTENT", mock_db)
        
        assert result is None
        mock_db.cases.find_one.assert_called_once()
    
    async def test_batch_update_scores(self, mock_db, mocker):
        """Test batch score updates"""
        # Mock find to return async iterator
        case_docs = [
            {
                "_id": "1",
                "case_id": "CASE-BATCH-001",
                "data": {
                    "patient_details": {"gender": "Male", "age_value": 25},
                    "medicine_details": [{"name": "Drug", "start_date": "2024-01-01"}],
                    "reaction_details": {"start_date": "2024-01-02"},
                    "severity": ["Mild"],
                    "description": "Test description one."
                }
            },
            {
                "_id": "2",
                "case_id": "CASE-BATCH-002",
                "data": {
                    "patient_details": {"gender": "Female", "age_value": 30},
                    "medicine_details": [{"name": "Drug2", "start_date": "2024-01-05"}],
                    "reaction_details": {"start_date": "2024-01-06"},
                    "severity": ["Moderate"],
                    "description": "Test description two."
                }
            }
        ]
        
        async def mock_find(*args, **kwargs):
            for doc in case_docs:
                yield doc
        
        mock_db.cases.find = mocker.MagicMock(return_value=mock_find())
        
        # Mock update_one
        mock_update_result = mocker.MagicMock()
        mock_update_result.modified_count = 1
        mock_db.cases.update_one = mocker.AsyncMock(return_value=mock_update_result)
        mock_db.cases.find_one = mocker.AsyncMock(side_effect=case_docs)
        
        # Execute
        summary = await batch_update_scores(mock_db)
        
        # Verify
        assert summary["total_processed"] == 2
        assert summary["successful"] == 2
        assert summary["failed"] == 0


class TestEdgeCases:
    """Test suite for edge cases and error handling"""
    
    @pytest.fixture
    def scorer(self):
        return VigiGradeScorer()
    
    def test_nested_none_values(self, scorer):
        """Test handling of None values in nested structures"""
        case = {
            "case_id": "CASE-NONE",
            "data": {
                "patient_details": None,
                "medicine_details": None,
                "reaction_details": None
            }
        }
        
        result = scorer.calculate_score(case)
        
        # Should handle gracefully without crashing
        assert isinstance(result["score"], (int, float))
        assert result["score"] >= 0.0
    
    def test_multiple_medicine_entries(self, scorer):
        """Test that only first medicine entry is evaluated"""
        case = {
            "case_id": "CASE-MULTI-MED",
            "data": {
                "patient_details": {
                    "gender": "Male",
                    "age_value": 25
                },
                "medicine_details": [
                    {
                        "name": "Drug1",
                        "start_date": None  # Missing
                    },
                    {
                        "name": "Drug2",
                        "start_date": "2024-01-01"  # Present
                    }
                ],
                "reaction_details": {
                    "start_date": "2024-01-02"
                },
                "severity": ["Mild"],
                "description": "Multiple medicines administered."
            }
        }
        
        result = scorer.calculate_score(case)
        
        # Should penalize for missing first medicine start date
        assert "medicine_details[0].start_date" in result["missing_fields"]
    
    def test_numeric_zero_not_treated_as_missing(self, scorer):
        """Test that numeric zero is valid for age"""
        case = {
            "case_id": "CASE-ZERO-AGE",
            "data": {
                "patient_details": {
                    "gender": "Male",
                    "age_value": 0  # Newborn
                },
                "medicine_details": [
                    {
                        "name": "TestDrug",
                        "start_date": "2024-01-01"
                    }
                ],
                "reaction_details": {
                    "start_date": "2024-01-02"
                },
                "severity": ["Mild"],
                "description": "Newborn patient case."
            }
        }
        
        result = scorer.calculate_score(case)
        
        # Age of 0 should be valid
        assert "patient_details.age_value" not in result["missing_fields"]
    
    def test_empty_string_description(self, scorer):
        """Test empty string description is penalized"""
        case = {
            "case_id": "CASE-EMPTY-DESC",
            "data": {
                "patient_details": {
                    "gender": "Male",
                    "age_value": 25
                },
                "medicine_details": [
                    {
                        "name": "TestDrug",
                        "start_date": "2024-01-01"
                    }
                ],
                "reaction_details": {
                    "start_date": "2024-01-02"
                },
                "severity": ["Mild"],
                "description": ""
            }
        }
        
        result = scorer.calculate_score(case)
        
        assert "description" in result["missing_fields"]
        assert result["score"] == 0.90


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
