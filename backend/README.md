# NOVA Backend

LangGraph-powered pharmacovigilance backend for adverse drug event reporting.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` and create `.env`:

```bash
cp .env .env
```

Edit `.env` with your credentials:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `MONGODB_URI` - MongoDB connection string
- Other optional configurations

### 3. Start MongoDB

Ensure MongoDB is running locally or update `MONGODB_URI` to point to your MongoDB instance.

```bash
# If using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using Python directly
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Process Message
```
POST /api/message
{
  "message": "I took aspirin and got a rash",
  "sender_phone": "+1234567890",
  "case_id": null
}
```

### Get Case State
```
GET /api/state/{case_id}
```

### Test Endpoints
```
POST /api/test/patient?message=I took aspirin and got a rash
POST /api/test/doctor?message=Reporting ADR: Patient on metformin 500mg BID
```

## Testing

### Run Graph Tests
```bash
python test/test_graph.py
```

### Test with cURL

**Patient Flow:**
```bash
curl -X POST http://localhost:8000/api/test/patient
```

**Doctor Flow:**
```bash
curl -X POST http://localhost:8000/api/test/doctor
```

**Custom Message:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I took aspirin and got a rash",
    "sender_phone": "+1234567890"
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API endpoints (deferred)
│   ├── doctor_workflow/
│   │   ├── nodes.yaml         # Doctor workflow definition
│   │   └── prompts/           # Doctor-specific prompts
│   ├── patient_workflow/
│   │   ├── nodes.yaml         # Patient workflow definition
│   │   └── prompts/           # Patient-specific prompts
│   ├── schemas/               # Pydantic models
│   ├── services/              # LLM, MongoDB, etc.
│   ├── shared_prompts/        # Shared prompts
│   ├── config.py              # Configuration
│   ├── state.py               # LangGraph state definition
│   ├── graph.py               # LangGraph orchestration
│   └── main.py                # FastAPI application
├── test/
│   └── test_graph.py          # Workflow tests
└── requirements.txt
```

## Workflow

### Patient Flow
1. Language Detection
2. User Type Detection → Patient
3. Patient Intake (simple language)
4. Document Intelligence (if documents uploaded)
5. Completeness Check
6. Clinical Triage
7. Confidence Scoring
8. Persist Case

### Doctor Flow
1. Language Detection
2. User Type Detection → Doctor
3. Doctor Registry Check
4. License Upload Request (if not verified)
5. Doctor Case Intake (clinical language)
6. Completeness Check
7. Clinical Triage
8. Confidence Scoring
9. Persist Case

## Configuration

Key settings in `config.py`:
- `GEMINI_TEXT_MODEL`: "gemini-2.0-flash-exp" (for text)
- `GEMINI_VISION_MODEL`: "gemini-1.5-flash" (for OCR)
- `REQUIRED_FIELDS`: ["drug_name", "symptoms", "timeline"]
- `COMPLETENESS_THRESHOLD`: 0.7
- `CONFIDENCE_THRESHOLD`: 0.6

## Development Notes

- **WhatsApp Integration**: Deferred - currently using REST API
- **Speech Module**: Deferred - text-only for now
- **Advanced AI Monitoring**: Deferred
- **Dashboard**: Deferred

## Troubleshooting

### MongoDB Connection Error
Ensure MongoDB is running and `MONGODB_URI` is correct.

### Gemini API Error
Check that `GEMINI_API_KEY` is valid and has quota.

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Next Steps

1. Test patient and doctor flows
2. Verify MongoDB persistence
3. Test with different languages
4. Add more comprehensive test cases
5. Integrate with frontend
