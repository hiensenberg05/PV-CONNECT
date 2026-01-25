# NOVA Backend - Quick Start Guide

## Prerequisites
- Python 3.10+
- MongoDB (local or remote)
- Google Gemini API key

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd d:\nova\backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file in `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=pv_connect
DEBUG=True
```

### 3. Start MongoDB
**Option A - Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option B - Local Installation:**
Ensure MongoDB service is running on port 27017

### 4. Start the Server
```bash
cd d:\nova\backend
uvicorn app.main:app --reload
```

Server will start at: `http://localhost:8000`

### 5. Test the API

**Open browser:**
- http://localhost:8000 - API info
- http://localhost:8000/docs - Interactive API docs (Swagger)

**Test patient flow:**
```bash
curl -X POST http://localhost:8000/api/test/patient
```

**Test doctor flow:**
```bash
curl -X POST http://localhost:8000/api/test/doctor
```

**Send custom message:**
```bash
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"I took aspirin and got a rash\", \"sender_phone\": \"+1234567890\"}"
```

## Verify Installation

Run the test script:
```bash
cd d:\nova\backend
python test/test_graph.py
```

Expected output:
- Language detection: `en`
- User type: `patient` or `doctor`
- Case ID generated
- Completeness and confidence scores
- Messages exchanged

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `docker ps` or check service status
- Verify `MONGODB_URI` in `.env`

**Gemini API Error:**
- Check API key is valid
- Verify you have API quota
- Test key at: https://aistudio.google.com/

**Import Errors:**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

## Next Steps

1. ✅ Test both patient and doctor workflows
2. ✅ Check MongoDB for persisted cases
3. ✅ Review logs for any errors
4. ✅ Test with different languages
5. ✅ Integrate with frontend

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/message` | POST | Process message |
| `/api/state/{case_id}` | GET | Get case state |
| `/api/test/patient` | POST | Test patient flow |
| `/api/test/doctor` | POST | Test doctor flow |

## Support

For issues or questions:
1. Check [README.md](file:///d:/nova/backend/README.md)
2. Review [walkthrough.md](file:///C:/Users/lenovo/.gemini/antigravity/brain/f59a1fa2-2957-4a7b-b1bb-3fc70121ae17/walkthrough.md)
3. Check logs in console output
