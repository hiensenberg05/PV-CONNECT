# PV Connect - AI-Assisted Pharmacovigilance System

PV Connect is an intelligent pharmacovigilance platform that enables seamless adverse event reporting through WhatsApp, powered by Google Gemini AI, MongoDB, and Cloudinary.

## 🎯 Overview

PV Connect simplifies adverse drug event reporting by allowing patients and healthcare professionals to report side effects via WhatsApp. The system uses AI to extract, validate, and process reports while ensuring regulatory compliance across different countries.

## 🏗️ Architecture

### Simplified Tech Stack
- **Frontend**: WhatsApp (Meta Cloud API)
- **Backend**: Python FastAPI + LangGraph
- **AI**: Google Gemini (all models)
- **Database**: MongoDB (text + vectors)
- **Storage**: Cloudinary (images + audio)
- **Dashboard**: React + Next.js

**No PostgreSQL. No S3. No Redis. No extra services.**

## 📋 Features

### Core Functionality
- ✅ **Multimodal Entry**: Text, voice, and image support via WhatsApp
- ✅ **Dynamic Language Detection**: Auto-detects and adapts to user's language
- ✅ **User Type Detection**: Distinguishes between patients and healthcare professionals
- ✅ **Automated Data Extraction**: AI-powered extraction of drug names, symptoms, severity
- ✅ **OCR Processing**: Extracts information from prescription images
- ✅ **Voice-to-Text**: Transcribes voice notes using Gemini
- ✅ **Compliance Checking**: Country-specific regulatory compliance validation
- ✅ **Clinical Triage**: AI-powered case prioritization
- ✅ **Signal Detection**: RAG-based safety signal identification
- ✅ **Real-time Dashboard**: WebSocket-powered live updates

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ installed
- Node.js 18+ installed
- MongoDB running locally or MongoDB Atlas account
- Cloudinary account
- WhatsApp Cloud API credentials
- Google Gemini API key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pvv
```

### 2. Backend Setup

#### Create Virtual Environment
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the root directory (`C:\Users\lenovo\Desktop\pvv\.env`):

```bash
# WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=pv_connect

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

#### Start Backend Server
```powershell
python run.py
```

Or using uvicorn directly:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### 3. Frontend Dashboard Setup

#### Navigate to Dashboard
```powershell
cd ..\dashboard
```

#### Install Dependencies
```powershell
npm install
```

#### Start Development Server
```powershell
npm run dev
```

Dashboard will be available at: http://localhost:3000

## 📁 Project Structure

```
pvv/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Environment configuration
│   │   ├── api/
│   │   │   ├── webhooks.py         # WhatsApp webhook handler
│   │   │   ├── dashboard.py        # Dashboard REST API
│   │   │   └── websockets.py       # WebSocket connections
│   │   ├── agents/
│   │   │   ├── graph.py            # LangGraph workflow
│   │   │   ├── state.py            # State schema
│   │   │   └── nodes/
│   │   │       ├── language_detection.py
│   │   │       ├── detect_user_type.py
│   │   │       ├── nlp_extraction.py
│   │   │       ├── ocr_processing.py
│   │   │       ├── voice_processing.py
│   │   │       ├── compliance_check.py
│   │   │       ├── clinical_triage.py
│   │   │       ├── followup_generator.py
│   │   │       ├── save_case.py
│   │   │       ├── send_response.py
│   │   │       ├── doctor_verification.py
│   │   │       └── signal_detection.py
│   │   ├── channels/
│   │   │   └── whatsapp.py         # WhatsApp message sender
│   │   ├── services/
│   │   │   ├── gemini_service.py   # Gemini AI integration
│   │   │   ├── mongodb_service.py  # MongoDB connection
│   │   │   ├── cloudinary_service.py # Cloudinary uploads
│   │   │   └── rag_service.py      # RAG vector search
│   │   └── models/
│   │       ├── case.py             # Case data models
│   │       └── user.py             # User data models
│   ├── requirements.txt
│   └── run.py
│
├── dashboard/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── page.tsx            # Main dashboard
│   │   │   └── cases/
│   │   │       └── [id]/
│   │   │           └── page.tsx   # Case detail page
│   │   ├── components/
│   │   │   ├── CaseList.tsx
│   │   │   ├── SignalAlerts.tsx
│   │   │   └── Analytics.tsx
│   │   └── hooks/
│   │       └── useWebSocket.ts    # WebSocket hook
│   ├── package.json
│   ├── next.config.js
│   └── tsconfig.json
│
├── .env                              # Environment variables (create from env_example)
├── env_example                       # Environment template
├── .gitignore
└── README.md
```

## 🔄 Workflow

### Patient Reporting Flow

1. **Initiation**: Patient sends message via WhatsApp
2. **Language Detection**: System detects language automatically
3. **User Type Detection**: Identifies if user is patient or doctor
4. **Data Extraction**: AI extracts drug name, symptoms, severity, etc.
5. **Compliance Check**: Validates against country-specific requirements
6. **Clinical Triage**: Prioritizes case based on severity
7. **Follow-up**: Generates questions for missing information
8. **Case Saving**: Stores case in MongoDB with vector embeddings
9. **Response**: Sends confirmation via WhatsApp

### Doctor Verification Flow

1. **Doctor Detection**: System identifies healthcare professional
2. **License Upload**: Doctor uploads medical license
3. **OCR Processing**: Extracts license details
4. **Verification**: Human-in-the-loop verification process
5. **Registry Update**: Adds to verified doctors database

## 🗄️ MongoDB Collections

- `cases` - Adverse event reports
- `messages` - Conversation history
- `users` - Doctor registry
- `drugs_database` - Drug validation data
- `compliance_templates` - Country-specific rules
- `audit_logs` - Audit trail
- `vectors` - RAG embeddings for signal detection

## 🔌 API Endpoints

### Health Check
```
GET /health
```

### WhatsApp Webhook
```
POST /webhook
```

### Dashboard API
```
GET /dashboard/cases
```

### WebSocket
```
WS /ws/dashboard
```

### API Documentation
```
GET /docs  # Swagger UI
```

## 🧪 Testing

### Test Backend Import
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python test_import.py
```

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

## 🔧 Configuration

### MongoDB Setup

**Local MongoDB:**
```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=pv_connect
```

**MongoDB Atlas:**
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=pv_connect
```

### Cloudinary Setup

1. Sign up at https://cloudinary.com
2. Get credentials from Dashboard
3. Add to `.env` file

### WhatsApp Cloud API Setup

1. Create Meta Developer account
2. Set up WhatsApp Business API
3. Get Phone Number ID and Access Token
4. Configure webhook URL: `https://your-domain.com/webhook`

## 📊 Dashboard Features

- Real-time case updates via WebSocket
- Signal alerts for safety concerns
- Analytics and reporting
- Case management interface

## 🛠️ Development

### Backend Development
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Frontend Development
```powershell
cd dashboard
npm run dev
```

## 🐛 Troubleshooting

### Import Errors
- Ensure all `__init__.py` files exist
- Activate virtual environment
- Install all dependencies

### MongoDB Connection Issues
- Verify MongoDB is running
- Check connection string in `.env`
- Ensure database exists

### Port Already in Use
- Change port in uvicorn command: `--port 8001`
- Or update Next.js port: `npm run dev -- -p 3001`

### Pillow Installation Issues
```powershell
pip install --upgrade pip setuptools wheel
pip install pillow
```

## 📝 Environment Variables

See `env_example` for all required environment variables.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- MongoDB for database
- Cloudinary for media storage
- Meta for WhatsApp Cloud API
- FastAPI and LangGraph communities

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ for better pharmacovigilance**
