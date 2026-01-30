# VigiGrade: Confidence Scoring Engine for Pharmacovigilance

A production-ready Python service that automatically calculates data completeness scores for adverse event reports in pharmacovigilance systems.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Scoring Algorithm](#scoring-algorithm)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Deployment](#deployment)
- [Configuration](#configuration)

---

## 🎯 Overview

VigiGrade is a background service that evaluates the completeness of pharmacovigilance case reports by analyzing critical data fields and calculating a confidence score from 0.0 (Poor) to 1.0 (Excellent).

### Key Capabilities

- **Automated Scoring**: Calculates completeness scores based on critical field presence
- **Real-time Updates**: Automatically updates scores when cases are modified
- **Batch Processing**: Efficiently processes multiple cases in parallel
- **RESTful API**: Clean HTTP endpoints for integration
- **Production Ready**: Comprehensive error handling, logging, and monitoring

---

## ✨ Features

### Core Functionality

- ✅ **Intelligent Field Assessment**: Evaluates patient demographics, medicine details, reaction information, severity, and descriptions
- ✅ **Granular Penalties**: Different penalty weights for different field types based on clinical importance
- ✅ **Quality Grades**: Classifies scores into Excellent, High, Moderate, Low, and Poor categories
- ✅ **Missing Field Tracking**: Identifies and reports all missing critical fields
- ✅ **Safe Navigation**: Handles nested dictionaries safely without crashes

### Background Worker

- 🔄 **Periodic Batch Updates**: Scheduled scoring of all cases
- 👁️ **Change Stream Monitoring**: Real-time updates when cases are modified
- 🔁 **Automatic Retries**: Exponential backoff for failed operations
- 📊 **Progress Tracking**: Detailed logging and statistics

### API Integration

- 🌐 **RESTful Endpoints**: FastAPI-based HTTP API
- 📝 **OpenAPI Documentation**: Auto-generated API docs
- 🔍 **Statistics Dashboard**: Aggregate score analytics
- 🎯 **Flexible Operations**: Calculate, update, or retrieve scores

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MongoDB Database                       │
│              (Adverse Event Reports)                     │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐           ┌─────▼─────┐
    │   API   │           │  Worker   │
    │ Service │           │  Service  │
    └────┬────┘           └─────┬─────┘
         │                      │
         │  ┌──────────────────┴────────────────────┐
         │  │                                        │
         └──▼──────────────────────────────────────┐ │
            │     VigiGrade Scoring Engine         │ │
            │  ┌────────────────────────────────┐  │ │
            │  │  • Field Assessment            │  │ │
            │  │  • Penalty Calculation         │  │ │
            │  │  • Grade Classification        │  │ │
            │  │  • Missing Field Detection     │  │ │
            │  └────────────────────────────────┘  │ │
            └──────────────────────────────────────┘ │
                                                      │
                                                      │
            ┌─────────────────────────────────────────┘
            │
            ▼
     ┌──────────────┐
     │  Update DB   │
     └──────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- pip or poetry

### Install Dependencies

```bash
# Using pip
pip install motor fastapi uvicorn pydantic pytest pytest-asyncio pytest-mock

# Using poetry
poetry add motor fastapi uvicorn pydantic
poetry add --group dev pytest pytest-asyncio pytest-mock
```

### Project Structure

```
app/
├── services/
│   └── scoring.py           # Core scoring engine
├── workers/
│   └── vigigrade_worker.py  # Background worker
├── api/
│   └── vigigrade.py         # FastAPI endpoints
└── __init__.py

tests/
└── test_scoring.py          # Unit tests
```

---

## 🚀 Quick Start

### 1. Basic Usage

```python
from app.services.scoring import VigiGradeScorer

# Initialize scorer
scorer = VigiGradeScorer()

# Calculate score for a case
case_data = {
    "case_id": "CASE-001",
    "data": {
        "patient_details": {
            "gender": "Male",
            "age_value": 25,
            "age_unit": "years"
        },
        "medicine_details": [
            {
                "name": "Paracetamol",
                "start_date": "2024-01-15"
            }
        ],
        "reaction_details": {
            "start_date": "2024-01-16"
        },
        "severity": ["Hospitalized"],
        "description": "Patient developed severe reaction."
    }
}

result = scorer.calculate_score(case_data)
print(f"Score: {result['score']}")  # 1.0
print(f"Grade: {result['grade']}")  # Excellent
```

### 2. Async Database Updates

```python
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.scoring import update_case_score

# Connect to MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.pharmacovigilance

# Update a specific case
result = await update_case_score("CASE-001", db)
print(f"Updated with score: {result['score']}")
```

### 3. Start Background Worker

```python
from app.workers.vigigrade_worker import initialize_worker
import asyncio

async def main():
    worker = await initialize_worker(
        mongodb_uri="mongodb://localhost:27017",
        database_name="pharmacovigilance",
        batch_interval_minutes=60
    )
    
    await worker.start(enable_change_stream=True)

asyncio.run(main())
```

### 4. Start API Server

```python
from fastapi import FastAPI
from app.api.vigigrade import router as vigigrade_router

app = FastAPI(title="Pharmacovigilance System")
app.include_router(vigigrade_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📚 API Reference

### Calculate Score (Without Saving)

**POST** `/api/v1/vigigrade/calculate`

Calculate score without updating the database.

```bash
curl -X POST http://localhost:8000/api/v1/vigigrade/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "CASE-001",
    "data": {
      "patient_details": {"gender": "Male", "age_value": 25},
      "medicine_details": [{"name": "Drug", "start_date": "2024-01-01"}],
      "reaction_details": {"start_date": "2024-01-02"},
      "severity": ["Mild"],
      "description": "Patient experienced mild reaction."
    }
  }'
```

**Response:**
```json
{
  "score": 1.0,
  "grade": "Excellent",
  "missing_fields": [],
  "penalty_breakdown": {}
}
```

### Update Case Score

**POST** `/api/v1/vigigrade/cases/{case_id}/update-score`

Calculate and save score to database.

```bash
curl -X POST http://localhost:8000/api/v1/vigigrade/cases/CASE-001/update-score
```

**Response:**
```json
{
  "case_id": "CASE-001",
  "score": 0.85,
  "grade": "High",
  "updated_at": "2024-01-30T10:30:00Z"
}
```

### Get Current Score

**GET** `/api/v1/vigigrade/cases/{case_id}/score`

Retrieve stored score without recalculation.

```bash
curl http://localhost:8000/api/v1/vigigrade/cases/CASE-001/score
```

### Batch Update

**POST** `/api/v1/vigigrade/batch-update`

Update multiple cases at once.

```bash
curl -X POST http://localhost:8000/api/v1/vigigrade/batch-update \
  -H "Content-Type: application/json" \
  -d '{
    "case_ids": ["CASE-001", "CASE-002", "CASE-003"]
  }'
```

**Response:**
```json
{
  "total_processed": 3,
  "successful": 3,
  "failed": 0,
  "errors": []
}
```

### Get Statistics

**GET** `/api/v1/vigigrade/statistics`

Aggregate score statistics.

```bash
curl http://localhost:8000/api/v1/vigigrade/statistics
```

**Response:**
```json
{
  "total_cases_scored": 150,
  "overall_average_score": 0.78,
  "distribution_by_grade": {
    "Excellent": {"count": 45, "percentage": 30.0, "avg_score": 0.95},
    "High": {"count": 60, "percentage": 40.0, "avg_score": 0.82},
    "Moderate": {"count": 30, "percentage": 20.0, "avg_score": 0.67},
    "Low": {"count": 10, "percentage": 6.7, "avg_score": 0.48},
    "Poor": {"count": 5, "percentage": 3.3, "avg_score": 0.25}
  }
}
```

---

## 🧮 Scoring Algorithm

### Base Score: 1.0 (Perfect)

### Penalty Table

| Missing Field | Penalty | Rationale |
|--------------|---------|-----------|
| `reaction_details.start_date` | **-0.20** | Critical for Time-to-Onset analysis |
| `medicine_details` (empty) | **-0.15** | No suspect drug identified |
| `medicine_details[0].start_date` | **-0.10** | Unknown therapy initiation |
| `patient_details.age_value` | **-0.10** | Demographics incomplete |
| `severity` (empty) | **-0.10** | Impact assessment missing |
| `description` (< 10 chars) | **-0.10** | Inadequate narrative |
| `patient_details.gender` | **-0.05** | Demographics incomplete |

### Grade Classification

| Score Range | Grade | Description |
|-------------|-------|-------------|
| 0.90 - 1.00 | **Excellent** | Complete, high-quality data |
| 0.75 - 0.89 | **High** | Minor gaps, suitable for analysis |
| 0.60 - 0.74 | **Moderate** | Some critical data missing |
| 0.40 - 0.59 | **Low** | Significant gaps present |
| 0.00 - 0.39 | **Poor** | Insufficient data quality |

### Empty/Missing Detection

Values considered missing:
- `None` or `null`
- Empty strings (`""` or whitespace only)
- `"Unknown"` (case-insensitive)
- Empty arrays (`[]`)
- Empty objects (`{}`)

---

## 💡 Usage Examples

### Example 1: Perfect Case

```python
perfect_case = {
    "case_id": "CASE-PERFECT",
    "data": {
        "patient_details": {
            "gender": "Male",
            "age_value": 25,
            "age_unit": "years"
        },
        "medicine_details": [{
            "name": "Paracetamol",
            "start_date": "2024-01-15"
        }],
        "reaction_details": {
            "start_date": "2024-01-16"
        },
        "severity": ["Hospitalized"],
        "description": "Detailed description of the adverse event."
    }
}

result = scorer.calculate_score(perfect_case)
# Score: 1.0, Grade: Excellent, Missing: []
```

### Example 2: Moderate Quality Case

```python
moderate_case = {
    "case_id": "CASE-MODERATE",
    "data": {
        "patient_details": {
            "gender": "Female",
            # age_value missing (-0.10)
        },
        "medicine_details": [{
            "name": "Aspirin"
            # start_date missing (-0.10)
        }],
        "reaction_details": {
            "start_date": "2024-01-20"
        },
        "severity": ["Mild"],
        "description": "Patient reported headache."
    }
}

result = scorer.calculate_score(moderate_case)
# Score: 0.80, Grade: High
# Missing: ["patient_details.age_value", "medicine_details[0].start_date"]
```

### Example 3: Poor Quality Case

```python
poor_case = {
    "case_id": "CASE-POOR",
    "data": {
        "patient_details": {},  # Empty
        "medicine_details": [],  # Empty (-0.15)
        "reaction_details": {},  # No start_date (-0.20)
        "severity": [],  # Empty (-0.10)
        "description": "Short"  # Too short (-0.10)
    }
}

result = scorer.calculate_score(poor_case)
# Score: 0.35, Grade: Poor
# Missing: All critical fields
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/test_scoring.py -v
```

### Run Specific Test

```bash
pytest tests/test_scoring.py::TestVigiGradeScorer::test_perfect_case_score -v
```

### Coverage Report

```bash
pytest tests/test_scoring.py --cov=app.services.scoring --cov-report=html
```

### Test Categories

1. **Unit Tests**: Core scoring logic
2. **Integration Tests**: MongoDB operations
3. **Edge Cases**: Null handling, empty values
4. **Error Handling**: Exceptions and retries

---

## 🚢 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["python", "-m", "app.workers.vigigrade_worker"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  vigigrade-worker:
    build: .
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
      - DATABASE_NAME=pharmacovigilance
      - BATCH_INTERVAL=60
    depends_on:
      - mongodb

  vigigrade-api:
    build: .
    command: uvicorn app.api.vigigrade:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
    depends_on:
      - mongodb

volumes:
  mongo_data:
```

### Environment Variables

```bash
# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=pharmacovigilance

# Worker Configuration
BATCH_INTERVAL_MINUTES=60
ENABLE_CHANGE_STREAM=true
MAX_RETRIES=3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

---

## ⚙️ Configuration

### Customize Penalties

```python
from app.services.scoring import VigiGradeScorer

# Modify penalty weights
scorer = VigiGradeScorer()
scorer.PENALTIES["reaction_start_date"] = 0.25  # Increase importance
scorer.PENALTIES["patient_gender"] = 0.02  # Decrease importance
```

### Adjust Grade Thresholds

```python
def _determine_grade(self, score: float) -> str:
    if score >= 0.95:  # Stricter Excellent threshold
        return DataQualityGrade.EXCELLENT
    elif score >= 0.80:
        return DataQualityGrade.HIGH
    # ... etc
```

### Custom Validation Rules

```python
def _assess_custom_field(self, data: Dict) -> tuple[float, List[str]]:
    """Add custom field validation"""
    penalty = 0.0
    missing = []
    
    reporter = data.get("reporter_details", {})
    if not reporter.get("qualification"):
        penalty += 0.08
        missing.append("reporter_details.qualification")
    
    return penalty, missing
```

---

## 📊 Monitoring & Logging

### Log Format

```
2024-01-30 10:30:15 - app.services.scoring - INFO - Calculated score for case CASE-001: 0.85 (High)
2024-01-30 10:31:20 - app.workers.vigigrade_worker - INFO - Batch update completed in 45.2s: 150 successful, 2 failed
```

### Metrics to Track

- Cases scored per hour
- Average score by time period
- Distribution of grades
- Failed update count
- Processing time per case

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact the development team
- Check the API documentation at `/docs`

---

## 🔄 Changelog

### Version 1.0.0 (2024-01-30)
- Initial release
- Core scoring engine
- Background worker
- RESTful API
- Comprehensive test suite
