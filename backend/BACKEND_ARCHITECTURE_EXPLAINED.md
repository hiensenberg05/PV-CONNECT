# Backend Architecture - Complete Explanation

## Overview

The NOVA Pharmacovigilance Assistant backend is a **LangGraph-powered FastAPI application** that processes adverse drug event reports through conversational workflows. It uses Google Gemini AI for natural language understanding and MongoDB for persistence.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│  (main.py) - REST API endpoints, request handling          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              LangGraph Workflow Engine                      │
│  (graph.py) - State machine orchestration                   │
│  - Nodes: Processing steps                                  │
│  - Edges: Conditional routing                              │
│  - State: NovaState (TypedDict)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐
│ LLM Service  │ │ MongoDB    │ │ Cloudinary│
│ (Gemini)     │ │ Service    │ │ Service   │
└──────────────┘ └────────────┘ └───────────┘
```

---

## Core Components

### 1. **FastAPI Application** (`main.py`)

**Purpose**: HTTP API server that handles incoming requests

**Key Endpoints**:
- `POST /api/message` - Process text messages
- `POST /api/upload` - Handle document/image uploads
- `GET /api/state/{case_id}` - Retrieve case state
- `GET /health` - Health check

**Lifecycle Management**:
- **Startup**: Connects to MongoDB
- **Shutdown**: Disconnects from MongoDB
- **CORS**: Configured to allow all origins (should be restricted in production)

**Request Flow**:
```python
1. Receive MessageInput (message, sender_phone, case_id)
2. Load existing state OR create new state
3. Invoke LangGraph workflow: graph_app.ainvoke(state)
4. Extract response from final state
5. Return MessageOutput (response, case_id, status)
```

---

### 2. **LangGraph Workflow** (`graph.py`)

**Purpose**: Orchestrates the conversation flow using a state machine

**State Definition** (`state.py`):
- `NovaState` - TypedDict containing all workflow data
- Fields: case_id, sender_type, extracted_data, messages, status, etc.
- State flows through nodes, each node can read/modify state

**Graph Structure**:
```python
workflow = StateGraph(NovaState)
workflow.set_entry_point("initial_classification")
# Nodes added with workflow.add_node()
# Edges added with workflow.add_edge() or workflow.add_conditional_edges()
```

**Key Nodes** (executed in order):

1. **`initial_classification_node`**
   - Detects language (ISO 639-1)
   - Asks user type (Patient/Doctor)
   - Generates case_id if new
   - Routes based on user type

2. **`patient_doc_request_node`**
   - **Patient-only**: Requests prescription/bill upload
   - Waits for image before proceeding
   - Acts as a gate

3. **`doctor_registry_check_node`**
   - Checks MongoDB for verified doctor
   - Sets `verified_doctor` flag
   - Routes to intake or license request

4. **`license_upload_request_node`**
   - Requests medical license upload
   - Uploads to Cloudinary
   - Sets `license_status` to "pending_verification"

5. **`document_extraction_node`**
   - Uses Gemini Vision API for OCR
   - Extracts: drug_name, dosage, symptoms, timeline
   - Merges with existing extracted_data

6. **`patient_intake_node`**
   - Conversational data collection (simple language)
   - Uses `patient_intake.txt` prompt
   - Extracts pharmacovigilance data from conversation
   - Handles rate limits gracefully

7. **`doctor_case_intake_node`**
   - Clinical data collection (medical terminology)
   - Uses `doctor_intake.txt` prompt
   - More structured, efficient for doctors

8. **`completeness_check_node`**
   - Validates required fields: drug_name, symptoms, timeline
   - Calculates completeness_score (0.0 - 1.0)
   - Routes:
     - If complete (≥0.7) → clinical_triage
     - If incomplete → loops back to intake OR doctor_handoff

9. **`clinical_triage_node`**
   - Uses RAG service to check known side effects
   - LLM classifies: "known", "unusual", or "severe"
   - Uses `clinical_triage.txt` prompt

10. **`confidence_scoring_node`**
    - Calculates confidence_score based on:
      - Completeness (60%)
      - Has timeline (20%)
      - Has dosage (20%)

11. **`persist_case_node`**
    - Saves final case to MongoDB
    - Marks status as "closed"
    - Converts state to CaseDocument schema

**Routing Functions**:
- `route_after_user_type()` - Patient vs Doctor routing
- `route_after_completeness()` - Complete vs Incomplete routing
- `route_after_registry_check()` - Verified vs Unverified routing

---

### 3. **LLM Service** (`services/llm_service.py`)

**Purpose**: Wrapper for Google Gemini API

**Key Methods**:
- `generate_text()` - Text generation with JSON schema support
- `extract_from_image()` - Vision API for OCR/document extraction
- `classify_initial_message()` - Combined language + user type detection

**Configuration**:
- Model: `gemini-2.5-flash` (text and vision)
- Temperature: 0.7
- Max tokens: 2048
- JSON mode: Enabled via `response_schema`

**Error Handling**:
- `RateLimitError` - Custom exception for 429/quota errors
- Graceful degradation when rate limits hit

**Usage Pattern**:
```python
response = await gemini_service.generate_text(
    prompt="User message",
    system_instruction=prompt_file_content,
    response_schema={"type": "object", "properties": {...}}
)
```

---

### 4. **MongoDB Service** (`services/mongodb_service.py`)

**Purpose**: Database operations using Motor (async MongoDB driver)

**Collections**:
- `cases` - Pharmacovigilance case documents
- `doctors` - Verified doctor registry
- `license_verifications` - License verification requests

**Key Methods**:
- `save_case()` - Upsert case document
- `get_case()` - Retrieve by case_id
- `check_doctor_registry()` - Check if doctor is verified
- `save_doctor()` - Add/update doctor in registry

**Connection Management**:
- Async connection via `AsyncIOMotorClient`
- Connected at startup, disconnected at shutdown
- Database name: `pv_connect` (from config)

---

### 5. **RAG Service** (`services/rag_service.py`)

**Purpose**: Drug safety database lookup (currently mock)

**Current Implementation**:
- Mock database with 3 drugs: aspirin, metformin, penicillin
- Simple string matching for side effects

**Methods**:
- `get_drug_side_effects()` - Get known side effects for drug
- `check_side_effect_match()` - Match reported symptoms to known effects

**Future Enhancement**:
- Replace with vector database (e.g., Pinecone, Weaviate)
- Load FDA/EMA drug safety databases
- Semantic search for better matching

---

### 6. **Cloudinary Service** (`services/cloudinary_service.py`)

**Purpose**: Image/document storage

**Features**:
- Upload images to Cloudinary
- Returns secure URLs
- Optional (gracefully handles missing config)

**Usage**:
- Document uploads (prescriptions, bills)
- License verification images

---

## Data Flow Examples

### Example 1: Patient Reporting ADR

```
1. User sends: "I took aspirin and got a rash"
   ↓
2. POST /api/message
   ↓
3. Create initial state:
   - case_id: "CASE-ABC123"
   - sender_phone: "+1234567890"
   - messages: [{"role": "user", "content": "I took aspirin..."}]
   ↓
4. initial_classification_node:
   - Detect language: "en"
   - Ask: "Are you a Patient or Doctor?"
   ↓
5. User responds: "Patient"
   ↓
6. patient_doc_request_node:
   - Ask: "Please upload prescription/bill"
   ↓
7. User uploads image
   ↓
8. document_extraction_node:
   - OCR: Extract drug_name="Aspirin", dosage="500mg"
   - Merge into extracted_data
   ↓
9. patient_intake_node:
   - Ask: "What symptoms are you experiencing?"
   ↓
10. User: "Rash and itching"
    ↓
11. completeness_check_node:
    - Check: drug_name ✓, symptoms ✓, timeline ✗
    - Score: 0.67 (< 0.7 threshold)
    - Route back to patient_intake_node
    ↓
12. patient_intake_node:
    - Ask: "When did the rash start?"
    ↓
13. User: "2 hours after taking"
    ↓
14. completeness_check_node:
    - Check: drug_name ✓, symptoms ✓, timeline ✓
    - Score: 1.0 (≥ 0.7)
    - Route to clinical_triage_node
    ↓
15. clinical_triage_node:
    - RAG: Check aspirin side effects → "rash" matches known
    - Classify: "known"
    ↓
16. confidence_scoring_node:
    - Score: 0.8 (completeness 1.0 * 0.6 + timeline 0.2 + dosage 0.2)
    ↓
17. persist_case_node:
    - Save to MongoDB
    - Status: "closed"
    ↓
18. Return response to user
```

### Example 2: Doctor Reporting ADR

```
1. User sends: "Reporting ADR: Patient on metformin 500mg BID developed hypoglycemia"
   ↓
2. initial_classification_node:
   - Detect language: "en"
   - User says: "Doctor"
   ↓
3. doctor_registry_check_node:
   - Check MongoDB: Is phone verified?
   - If YES → doctor_case_intake_node
   - If NO → license_upload_request_node
   ↓
4. license_upload_request_node:
   - Ask: "Please upload medical license"
   - User uploads license image
   - Upload to Cloudinary
   - Set license_status: "pending_verification"
   ↓
5. doctor_case_intake_node:
   - Use clinical terminology prompt
   - Ask: "Patient demographics and severity?"
   ↓
6. User: "65F, moderate severity, BG 55 mg/dL"
   ↓
7. completeness_check_node:
   - Extract: drug_name, symptoms, timeline
   - If complete → clinical_triage
   - If incomplete → loop back
   ↓
8. [Continue through triage → scoring → persist]
```

---

## State Management

**State Persistence**:
- State saved to MongoDB at key points:
  - After initial classification
  - After each intake node
  - After completeness check
  - Final persist

**State Continuity**:
- If `case_id` provided in request, load existing state
- Append new message to existing messages
- Continue from `current_node`

**State Structure**:
```python
{
    "case_id": "CASE-ABC123",
    "sender_phone": "+1234567890",
    "sender_type": "patient",
    "language": "en",
    "extracted_data": {
        "drug_name": "Aspirin",
        "drug_dosage": "500mg",
        "symptoms": ["rash", "itching"],
        "timeline": "2 hours after taking"
    },
    "messages": [
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "timestamp": "..."}
    ],
    "completeness_score": 1.0,
    "confidence_score": 0.8,
    "status": "open",
    "current_node": "clinical_triage"
}
```

---

## Configuration (`config.py`)

**Environment Variables**:
- `GEMINI_API_KEY` - Required
- `MONGODB_URI` - Default: "mongodb://localhost:27017"
- `MONGODB_DATABASE` - Default: "pv_connect"
- `CLOUDINARY_*` - Optional

**Workflow Settings**:
- `REQUIRED_FIELDS`: ["drug_name", "symptoms", "timeline"]
- `COMPLETENESS_THRESHOLD`: 0.7
- `CONFIDENCE_THRESHOLD`: 0.6

---

## Error Handling

**Rate Limiting**:
- Catches Gemini API 429 errors
- Raises `RateLimitError`
- Nodes handle gracefully: Save state, return error message

**Database Errors**:
- Logged but don't crash workflow
- State still flows through nodes

**Missing Data**:
- Nodes check for required data before processing
- Default values used when appropriate

---

## Key Design Decisions

1. **LangGraph Over Pure FastAPI**:
   - Complex state machine needs
   - Conditional routing
   - Human-in-the-loop workflows

2. **State-Based Architecture**:
   - All data in NovaState
   - Nodes are pure functions (state → state)
   - Easy to debug and test

3. **Prompt Files vs Hardcoded**:
   - Prompts in `.txt` files for easy editing
   - Loaded at runtime
   - Version controlled

4. **Separate Patient/Doctor Flows**:
   - Different language complexity
   - Different verification requirements
   - Different data collection style

5. **Document Upload First (Patients)**:
   - OCR can extract structured data
   - Reduces conversation length
   - Better data quality

---

## Testing

**Test Endpoints**:
- `POST /api/test/patient` - Test patient flow
- `POST /api/test/doctor` - Test doctor flow

**Manual Testing**:
```bash
# Start server
uvicorn app.main:app --reload

# Test patient flow
curl -X POST http://localhost:8000/api/test/patient

# Test with custom message
curl -X POST http://localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "I took aspirin and got a rash", "sender_phone": "+1234567890"}'
```

---

## Future Enhancements

1. **YAML-Driven Workflows**:
   - Currently YAML files are documentation
   - Could be parsed to dynamically create nodes

2. **Real RAG Database**:
   - Replace mock drug database
   - Vector search for better matching

3. **WhatsApp Integration**:
   - Webhook endpoints exist but empty
   - Need to implement WhatsApp Business API

4. **Advanced Monitoring**:
   - Dashboard endpoints exist but empty
   - Real-time case tracking

5. **Multi-language Support**:
   - Language detection works
   - Prompts need translation

---

## Summary

The backend is a **sophisticated conversational AI system** that:
- Uses LangGraph for workflow orchestration
- Leverages Gemini AI for NLP and OCR
- Persists state in MongoDB
- Handles both patient and doctor workflows
- Extracts structured pharmacovigilance data
- Performs clinical triage and scoring
- Saves complete case documents

**Key Strengths**:
- Modular architecture (services, schemas, nodes)
- Error handling and rate limit management
- State persistence for continuity
- Extensible design (easy to add nodes)

**Current Status**:
- ✅ Core workflow functional
- ✅ Patient flow working
- ✅ Doctor flow working
- ✅ Document extraction working
- ⏳ WhatsApp integration pending
- ⏳ Dashboard pending
- ⏳ Real RAG database pending
