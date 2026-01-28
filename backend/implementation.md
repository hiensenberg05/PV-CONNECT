# PV-CONNECT Backend Implementation Guide

This document captures the implementation details, directory structure, data schemas, and workflow logic of the PV-CONNECT backend. It is intended to serve as the Source of Truth for the system.

## 1. System Overview
The backend is a **deterministic, state-driven workflow engine** designed to collect Pharmacovigilance (PvPI) data via WhatsApp. It strictly separates **Decision Logic** (Engine) from **Execution** (Partner/Services).

---

## 2. Workflow & Concepts

### **Patient Workflow**
1.  **Initiation**: User initiates chat via link (email/SMS/WhatsApp).
2.  **Language Detection**: System detects language (can change anytime).
3.  **Data Collection (7 Sections)**: The engine iterates through the PvPI form:
    *   **Section 1**: Patient Details (initials, gender, age).
    *   **Section 2**: Health Information (reason for medicine, who advised).
    *   **Section 3**: Reporter Details (name, address, phone, email).
    *   **Section 4**: Medicine Details (name, quantity, dosage, dates) - **REPEATABLE**.
    *   **Section 5**: Side Effect Details (start date, continuing, stop date).
    *   **Section 6**: Severity (multiple selection allowed).
    *   **Section 7**: Description (detail, management action).
4.  **OCR Handling**: Accepts documents (prescription/bill) anytime. Merges extracted textual data with the conversation state.
5.  **Gap Filling**: Asks minimal follow-up questions for missing fields.
6.  **Case Generation**: Generates `case_id` when complete (or partial). User can share this ID with a doctor.

### **Doctor Workflow**
1.  **Access**: Doctor enters via link or provides `case_id`.
2.  **Verification**:
    *   System checks if the doctor is in the database.
    *   **If not verified**: Request license -> Trigger Async Human Verification -> Chat continues while pending.
    *   **If rejected**: Gracefully restrict access.
3.  **Case Loading**: If `case_id` is provided, the system loads the existing patient case.
4.  **Clinical Input**: Collects medical information in proper order.
5.  **Updates**: Updates the case continuously with new notes/data.

### **Key Challenge: Question Tracking**
The core ambiguity in conversational flows is tracking:
1.  What has been asked?
2.  What has been answered?
3.  What still needs to be asked?
4.  What can be skipped based on OCR/AI extraction?

**Solution**: The system uses **State-Driven Question Tracking** with a `field_status` dictionary for every field to track `asked`, `answered`, `value`, and `source`.

### **Field Registry Concept**
Each field in the PvPI form is defined by static metadata in `field_registry.py`:
*   `section`: Which section (1-7).
*   `required`: Boolean.
*   `question_en` / `question_hi`: Localized question text.
*   `options`: For select/multiselect constraints.
*   `extractable_from_ocr`: Whether it can be filled via document upload.
*   `depends_on`: Conditional logic (e.g., only ask "Hospital Name" if "Hospitalized" is Yes).
*   `field_type`: text, select, multiselect, date, phone, etc.
*   `repeatable`: Handles lists (e.g., multiple medicines).
*   `prefill_from`: Auto-fills from metadata (e.g., `phone_number`).

---

## 3. Project Structure

```text
c:\PV-CONNECT\backend
├── app
│   ├── api
│   │   └── webhooks.py          # Entry point for WhatsApp Webhooks
│   ├── db
│   │   ├── mongo_db.py          # MongoDB Async Driver (Motor) wrapper
│   │   └── cloudinary_service.py # (Planned) Media handling
│   ├── schemas
│   │   ├── case.py              # Final Case DB Model
│   │   ├── conversation_state.py # Runtime Memory Model
│   │   ├── field_registry.py    # Static Definition of PvPI Questions
│   │   ├── message.py           # I/O Schemas (MessageIn/Out)
│   │   ├── pvpi.py              # PvPI Nested Form Structure
│   │   ├── user.py              # User Registry Model
│   │   └── workflow_action.py   # Action Intents (CALL_AI, SAVE_DB)
│   ├── workflows
│   │   ├── doctor
│   │   │   └── engine.py        # Doctor Workflow Logic
│   │   ├── patient
│   │   │   └── engine.py        # Patient Workflow Logic
│   │   ├── questionmanager.py   # Decisions on "What to ask next?"
│   │   ├── router.py            # Routes User -> Workflow
│   │   ├── test_full_simulation.py # E2E Integration Test
│   │   └── test_workflow.py     # Unit Tests
│   ├── config.py                # Pydantic Settings (.env loader)
│   └── main.py                  # FastAPI Application Entry
├── requirements.txt             # Python Dependencies
├── .env                         # Environment Variables (Secrets)
└── implementation.md            # This Documentation
```

---

## 4. Data Architectures (JSON Schemas)

### **A. Input Format (MessageIn)**
Incoming webhook payload is normalized into this structure before processing.
```json
{
  "phone_number": "919999999999",
  "message_type": "text",  // or "image", "audio", "document"
  "text_content": "Dolo 650",
  "timestamp": "2026-01-28T14:30:00.000Z",
  "whatsapp_message_id": "wamid.HBgM...",
  "media_id": null,        // if message_type != text
  "metadata": { "user_type": "patient" }
}
```

### **B. Output Format (MessageOut)**
The response sent back to the WhatsApp wrapper.
```json
{
  "text": "What is the name of the medicine?",
  "requires_input": true,
  "buttons": ["Option A", "Option B"],
  "show_file_upload": false,
  "language": "en"
}
```

### **C. Conversational State (`ConversationState`)**
This is the "Brain" of the bot. It is loaded from Redis/Memory at the start of a turn and saved at the end.

```json
{
  "case_id": "ea401880-eecb-4927-ac1d-3594afe84406",
  "user_type": "patient",
  "phone_number": "919999999999",
  
  // LOGIC FLAGS
  "workflow_stage": "COLLECTING", // INIT, COLLECTING, COMPLETE
  "doctor_verified": false,       // Doctor Only
  "awaiting_license": false,      // Doctor Only

  // DATA ACCUMULATION
  "missing_fields": ["medicine_name", "severity"],
  "extracted_data": {
    "patient_initials": "JD",
    "reason_for_medicine": "Fever",
    "medicine_name": "Dolo 650"
  },
  
  // CURRENT TURN CONTEXT
  "current_message": "Dolo 650", 
  "document_current_uploaded": false
}
```

### **D. Final Database Object (`Case`)**
Stored in MongoDB collection `cases`.
```json
{
  "_id": "ObjectId(...)",
  "case_id": "ea401880-eecb-4927-ac1d-3594afe84406",
  "patient_phone": "919999999999",
  "reporter_type": "patient", // "patient" or "doctor"
  "is_complete": true,
  "created_at": "2026-01-28T14:35:41.910Z",
  "updated_at": "2026-01-28T14:35:41.910Z",
  "data": {
    "patient_initials": "JD",
    "patient_age": "45",
    "patient_gender": "Male",
    "reason_for_medicine": "Fever",
    "who_advised_medicine": "Doctor",
    "reporter_name": "John Doe",
    "reporter_phone": "9999999999",
    "medicine_name": "Dolo 650",
    "medicine_dosage": "No",
    "side_effect_description": "Rash",
    "hospitalized": "No",
    "severity": "Mild",
    "management_action": "Stopped medicine"
  }
}
```

---

## 5. Technical Implementation Details

**Configuration & Dependencies**
*   **Core Libraries**: `fastapi`, `uvicorn`, `motor`, `pydantic`, `pydantic-settings`.
*   **MongoDB**: Configured with `uuidRepresentation="standard"` for correct UUID handling.

**The Engine Loop (Implementation)**
1.  **Receive Message**: User sends text/audio/image.
2.  **Update State**: `current_message` is updated in `ConversationState`.
3.  **Action Emission**:
    *   If Audio/Image -> Emit `CALL_STT` or `CALL_OCR`.
    *   If Text -> Emit `CALL_AI_EXTRACT` (Logic: "Extract current missing field from text").
4.  **Partner Execution (Simulated/Real)**:
    *   AI Service processes text.
    *   Updates `extracted_data` in State with found fields using `QuestionManager.mark_field_answered()`.
5.  **Calculate Next Step**:
    *   `QuestionManager` scans `FIELD_REGISTRY`.
    *   Finds first field where `required=True` AND status is not `answered`.
6.  **Response**: Return the `question_en` or `question_hi` string for that missing field.

**Testing & Simulation**
The file `app/workflows/test_full_simulation.py` is the primary verification tool.
*   **Mocks AI**: Loopback "AI Extracted Answer".
*   **Mocks Async Verification**: Simulates license check delays.
*   **Real Database Write**: Connects to the configured MongoDB and saves the final result.

**Usage:**
```bash
python app/workflows/test_full_simulation.py
```
