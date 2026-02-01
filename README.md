# NOVA

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" />
</p>

**NOVA** is a Pharmacovigilance (PV) reporting system that enables patients and healthcare providers to report adverse drug reactions (ADRs) via WhatsApp. The system uses AI-powered data extraction and BCPNN signal detection for drug safety analytics.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Credentials Setup](#-api-credentials-setup)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [Docker Deployment](#-docker-deployment)
- [API Documentation](#-api-documentation)

---

## 🎯 Features

- **WhatsApp Integration**: Report ADRs via WhatsApp Business API
- **AI-Powered Data Extraction**: Uses Groq LLM for intelligent field extraction
- **OCR Support**: Extract data from prescription images using Gemini Vision
- **Voice Transcription**: Convert voice messages to text using AssemblyAI
- **BCPNN Signal Detection**: Analyze drug-event pairs for safety signals
- **VigiGrade Scoring**: Quality assessment of case reports
- **Doctor Verification**: License verification workflow for healthcare providers
- **Real-time Dashboard**: Analytics dashboard with case management

---

## 📁 Project Structure

```
PV-CONNECT/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── agents/            # AI agents for data processing
│   │   ├── analytics/         # BCPNN engine & VigiGrade scoring
│   │   │   ├── bcpnn_engine.py
│   │   │   ├── vigigrade.py
│   │   │   ├── analyze_faers.py
│   │   │   └── faers_random_1000.xlsx
│   │   ├── api/               # API route handlers
│   │   │   ├── webhooks.py    # WhatsApp webhook
│   │   │   ├── cases.py       # Case management
│   │   │   ├── analytics.py   # Analytics endpoints
│   │   │   └── auth.py        # Authentication
│   │   ├── data/              # Prompt templates
│   │   ├── db/                # Database services
│   │   │   ├── mongo_db.py
│   │   │   └── cloudinary_service.py
│   │   ├── schemas/           # Pydantic models
│   │   ├── services/          # Business logic
│   │   │   ├── llm_service.py
│   │   │   ├── ocr_service.py
│   │   │   └── voice_service.py
│   │   ├── utils/             # Utility functions
│   │   ├── workflows/         # Conversation workflows
│   │   │   ├── keep_workflow.py
│   │   │   ├── cache_store.py
│   │   │   └── state_save.py
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI application
│   └── requirements.txt
│
├── Frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── api/               # API client functions
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .env                        # Environment variables
├── .gitignore
├── Dockerfile                  # Docker configuration
└── README.md
```

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| MongoDB | 6.0+ | Database (or use MongoDB Atlas) |
| Redis | 7.0+ | Session caching (optional) |
| FFmpeg | Latest | Audio processing for voice messages |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/PV-CONNECT.git
cd PV-CONNECT
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

> **Note**: For audio processing, you also need FFmpeg:
> - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
> - **Linux**: `sudo apt install ffmpeg`
> - **Mac**: `brew install ffmpeg`

### 4. Install Frontend Dependencies

```bash
cd ../Frontend
npm install
```

### 5. Configure Environment Variables

```bash
cd ..
cp env_example.txt .env
# Edit .env with your credentials
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# ============================================
# WHATSAPP BUSINESS API
# ============================================
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token

# ============================================
# DATABASE
# ============================================
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DATABASE=pv_connect

# ============================================
# CLOUD STORAGE (Cloudinary)
# ============================================
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# ============================================
# AI/LLM APIs
# ============================================
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

# ============================================
# SPEECH-TO-TEXT
# ============================================
ASSEMBLY_API_KEY=your_assemblyai_key
```

---

## 🔑 API Credentials Setup

### WhatsApp Business API

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app → Select "Business" type
3. Add the **WhatsApp** product to your app
4. Go to **WhatsApp** → **API Setup**
5. Get your:
   - **Phone Number ID**: Found in the API Setup page
   - **Access Token**: Generate a temporary token (expires in 24h) or create a System User for permanent token
   - **Verify Token**: Create any custom string for webhook verification

6. Configure Webhook:
   - Webhook URL: `https://your-domain.com/webhook`
   - Verify Token: Same as `WHATSAPP_VERIFY_TOKEN` in `.env`
   - Subscribe to: `messages`

> **Important**: For production, create a System User in Business Settings → System Users → Generate Token with `whatsapp_business_messaging` permission.

---

### MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user
4. Whitelist your IP (or `0.0.0.0/0` for development)
5. Get the connection string and update `MONGODB_URI`

---

### Cloudinary (Media Storage)

1. Go to [Cloudinary](https://cloudinary.com/)
2. Sign up for a free account
3. Go to Dashboard → Copy:
   - Cloud Name
   - API Key
   - API Secret

---

### Groq API (LLM)

1. Go to [Groq Console](https://console.groq.com/)
2. Create an account
3. Generate an API key
4. Model used: `llama-3.3-70b-versatile`

---

### Google Gemini API (OCR)

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Model used: `gemini-2.0-flash-exp`

---

### AssemblyAI (Speech-to-Text)

1. Go to [AssemblyAI](https://www.assemblyai.com/)
2. Create an account
3. Generate an API key

---

## 🗄️ Database Setup

### Collections Structure

The application uses the following MongoDB collections:

| Collection | Purpose |
|------------|---------|
| `cases` | Completed PV case reports |
| `conversation_states` | Active conversation sessions |
| `employees` | Registered healthcare providers |
| `faers_cases` | FAERS dataset for analytics |
| `analytics_signals` | BCPNN signal detection results |

### Initialize FAERS Data

After starting the backend, trigger FAERS data ingestion:

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/analytics/ingest-faers

# Or using PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analytics/ingest-faers" -Method POST
```

---

## 🏃 Running the Application

### Start Backend (Development)

```bash
cd backend
..\venv\Scripts\activate  # Windows
# source ../venv/bin/activate  # Linux/Mac

uvicorn app.main:app --reload --port 8000
```

### Start Frontend (Development)

```bash
cd Frontend
npm run dev
```

### Access the Application

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Frontend Dashboard | http://localhost:5173 |

---

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t pv-connect .

# Run the container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name pv-connect \
  pv-connect
```

### Docker Compose (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - redis

  frontend:
    build: ./Frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

Run with:
```bash
docker-compose up -d
```

---

## 📚 API Documentation

Once the backend is running, access the interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET/POST | `/webhook` | WhatsApp webhook |
| GET | `/api/cases` | List all cases |
| GET | `/api/v1/analytics/signals` | Get BCPNN signals |
| GET | `/api/v1/analytics/stats` | Get analytics stats |
| POST | `/api/v1/vigigrade/score` | Calculate VigiGrade score |

---

## 🔧 Troubleshooting

### Common Issues

1. **WhatsApp messages not being received**
   - Check webhook URL is publicly accessible
   - Verify the `WHATSAPP_VERIFY_TOKEN` matches
   - Check Meta webhook subscription is active

2. **MongoDB connection failed**
   - Verify IP is whitelisted in Atlas
   - Check connection string format
   - Ensure database user has correct permissions

3. **OCR not working**
   - Verify `GEMINI_API_KEY` is valid
   - Check Cloudinary is properly configured
   - Ensure image format is supported (jpg, png, webp)

4. **Voice transcription failing**
   - Verify `ASSEMBLY_API_KEY` is valid
   - Check FFmpeg is installed and in PATH
   - Ensure audio format is supported

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

For questions or support, please open an issue on GitHub.
