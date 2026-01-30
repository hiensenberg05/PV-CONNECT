# VigiGrade Quick Start Guide

Get started with VigiGrade in 5 minutes!

## Installation

```bash
# Clone or download the code
pip install -r requirements.txt
```

## Option 1: Standalone Scoring (No Database)

```python
from app.services.scoring import VigiGradeScorer

# Create scorer
scorer = VigiGradeScorer()

# Your case data
case = {
    "case_id": "CASE-001",
    "data": {
        "patient_details": {
            "gender": "Male",
            "age_value": 25
        },
        "medicine_details": [
            {"name": "Paracetamol", "start_date": "2024-01-15"}
        ],
        "reaction_details": {
            "start_date": "2024-01-16"
        },
        "severity": ["Mild"],
        "description": "Patient experienced mild headache."
    }
}

# Calculate score
result = scorer.calculate_score(case)

# View results
print(f"Score: {result['score']}")  # e.g., 1.0
print(f"Grade: {result['grade']}")  # e.g., "Excellent"
print(f"Missing: {result['missing_fields']}")  # e.g., []
```

## Option 2: With MongoDB Integration

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.scoring import update_case_score

async def update_case():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.pharmacovigilance
    
    # Update a specific case
    result = await update_case_score("CASE-001", db)
    
    print(f"Score: {result['score']}")
    print(f"Grade: {result['grade']}")
    
    client.close()

# Run
asyncio.run(update_case())
```

## Option 3: Background Worker (Automated)

```bash
# Start the worker
python -m app.workers.vigigrade_worker
```

The worker will:
- ✅ Run batch updates every 60 minutes
- ✅ Auto-update when cases are modified
- ✅ Handle errors with automatic retries

## Option 4: REST API

```bash
# Start API server
uvicorn app.api.vigigrade:app --reload
```

Then use the endpoints:

```bash
# Calculate score
curl -X POST http://localhost:8000/api/v1/vigigrade/calculate \
  -H "Content-Type: application/json" \
  -d '{"case_id": "CASE-001", "data": {...}}'

# Update case score in database
curl -X POST http://localhost:8000/api/v1/vigigrade/cases/CASE-001/update-score

# Get statistics
curl http://localhost:8000/api/v1/vigigrade/statistics
```

## What Gets Scored?

VigiGrade checks for these critical fields:

| Field | Missing Penalty | Why It Matters |
|-------|----------------|----------------|
| Reaction start date | -0.20 | Time-to-onset analysis |
| Medicine details | -0.15 | Identify suspect drug |
| Medicine start date | -0.10 | Therapy timeline |
| Patient age | -0.10 | Demographics |
| Severity | -0.10 | Impact assessment |
| Description (10+ chars) | -0.10 | Case narrative |
| Patient gender | -0.05 | Demographics |

## Score Interpretation

| Score | Grade | Meaning |
|-------|-------|---------|
| 0.90-1.00 | Excellent | Complete data ✅ |
| 0.75-0.89 | High | Minor gaps 👍 |
| 0.60-0.74 | Moderate | Some data missing ⚠️ |
| 0.40-0.59 | Low | Significant gaps ❌ |
| 0.00-0.39 | Poor | Insufficient data ⛔ |

## Database Updates

After scoring, your MongoDB documents will have:

```json
{
  "_id": "...",
  "case_id": "CASE-001",
  "data": {...},
  
  // NEW FIELDS ADDED BY VIGIGRADE:
  "confidence_score": 0.85,
  "data_quality_report": {
    "grade": "High",
    "missing": ["patient_details.age_value"],
    "penalty_breakdown": {
      "patient": 0.10
    },
    "calculated_at": "2024-01-30T10:30:00Z"
  }
}
```

## Running Examples

```bash
# Run all demo examples
python examples/demo.py
```

This will demonstrate:
1. Basic scoring
2. Async operations
3. Database integration
4. Batch processing
5. Statistics
6. Custom penalties
7. Edge case handling

## Customization

### Change Penalty Weights

```python
scorer = VigiGradeScorer()
scorer.PENALTIES["reaction_start_date"] = 0.30  # Increase importance
scorer.PENALTIES["patient_gender"] = 0.02       # Decrease importance
```

### Modify Batch Interval

```python
# Worker runs every 30 minutes instead of 60
worker = VigiGradeWorker(db, batch_interval_minutes=30)
```

## Troubleshooting

**Problem: "Case not found"**
- Ensure the case_id exists in your database
- Check MongoDB connection string

**Problem: "Score is 0.0 for all cases"**
- Verify the `data` field exists in your documents
- Check field names match exactly (case-sensitive)

**Problem: Worker not updating cases**
- Ensure MongoDB replica set is configured (required for change streams)
- Check worker logs for errors

## Next Steps

1. ✅ Test with your actual case data
2. ✅ Review the scoring algorithm
3. ✅ Customize penalties for your needs
4. ✅ Set up monitoring and logging
5. ✅ Deploy to production

For detailed documentation, see `README.md`.

## Support

- 📖 Full Documentation: `README.md`
- 🧪 Tests: `pytest tests/test_scoring.py -v`
- 🔍 API Docs: `http://localhost:8000/docs` (when API is running)
- 💡 Examples: `examples/demo.py`
