# NOVA – Advanced AI Pharmacovigilance Assistant

NOVA is a LangGraph-powered, multimodal pharmacovigilance system designed
to enable frictionless adverse drug event reporting via WhatsApp.

It supports both **patients** and **healthcare professionals**, ensures
regulatory completeness, and provides AI-assisted safety monitoring
for pharmacovigilance teams.

---

## 🧠 Core Capabilities

- WhatsApp-based conversational reporting
- Multilingual support with dynamic language detection
- Patient and doctor-specific workflows
- Human-in-the-loop verification for healthcare professionals
- Document intelligence for prescriptions and bills
- Clinical triage against known drug safety data
- Confidence and completeness scoring
- Continuous AI-driven safety monitoring

---

## 📁 Project Structure

NOVA/
├── backend/
│ └── app/
│ ├── api/
│ │ ├── advanced_aimonitoring/
│ │ │ ├── analysis.py
│ │ │ ├── cases.py
│ │ │ └── dashboard.py
│ │ ├── webhooks.py
│ │ ├── websockets.py
│ │ └── whatsapppconnection.py
│ │
│ ├── doctor_workflow/
│ │ ├── nodes.yaml
│ │ └── prompts/
│ │
│ ├── patient_workflow/
│ │ ├── nodes.yaml
│ │ └── prompts/
│ │
│ ├── schemas/
│ │ ├── case_schemas.py
│ │ ├── doctor_schemas.py
│ │ └── message_schemas.py
│ │
│ ├── services/
│ │ ├── llm_service.py
│ │ ├── mongodb_service.py
│ │ ├── cloudinary_service.py
│ │ └── rag_service.py
│ │
│ ├── shared_prompts/
│ │
│ ├── graph.py
│ ├── state.py
│ ├── config.py
│ └── main.py
│
├── test/
│ ├── test_graph.py
│ └── testing_gemini.ipynb
│
├── .env
├── env_example.txt
└── README.md

yaml
Copy code

---

## 🔄 Workflow Overview

### Phase 1 – Initiation & Identity
- Language detection
- Patient vs Doctor classification
- Doctor registry check
- Async human license verification

### Phase 2 – Data Extraction
- Conversational intake
- OCR and document intelligence
- Country-specific compliance mapping
- Minimal follow-up logic

### Phase 3 – Clinical Triage
- Side-effect comparison using internal drug database
- Identification of unusual or severe cases
- Case ID handover for doctor continuation

### Phase 4 – Safety Intelligence
- Confidence scoring
- Structured case storage
- Non-LLM AI monitoring for trend and spike detection
- Dashboard-ready outputs

---

## 🧩 Architectural Principles

- LangGraph-based stateful orchestration
- YAML-driven workflow definitions
- Prompts isolated from application logic
- Human-in-the-loop where required
- Analytics separated from LLM reasoning
- Audit-ready structured data models

---

## 🚀 Execution Strategy

The system is implemented incrementally:
1. Phase 1 nodes tested via dummy frontend
2. Document intelligence and triage added
3. Monitoring and dashboard enabled
4. WhatsApp production integration

---

## ⚠️ Disclaimer

This system assists pharmacovigilance workflows.
It does not replace medical judgment or regulatory authority.