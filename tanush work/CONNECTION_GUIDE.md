# PV Connect - Connection Guide

## ✅ Backend-Frontend Connection Status

All services are now properly connected and configured!

### 🔌 Backend Services

#### 1. **MongoDB Connection**
- **Status**: ✅ Connected via `motor` (async MongoDB driver)
- **Configuration**: Loaded from `.env` file (`MONGODB_URI`, `MONGODB_DATABASE`)
- **Initialization**: Automatically connects on FastAPI startup
- **Location**: `backend/app/services/mongodb_service.py`

#### 2. **FastAPI Backend**
- **Status**: ✅ Running on `http://localhost:8000` (default)
- **CORS**: ✅ Configured to allow all origins (for development)
- **Health Check**: `GET /health`
- **Location**: `backend/app/main.py`

#### 3. **API Endpoints**

**Test Endpoints (for frontend):**
- `POST /api/test/message` - Send message to LangGraph workflow
- `GET /api/test/case/{case_id}` - Retrieve case state

**Dashboard Endpoints:**
- `GET /dashboard/cases` - List all cases (with pagination)
- `GET /dashboard/cases/{case_id}` - Get specific case

**Webhook Endpoints:**
- `GET /webhook` - WhatsApp webhook verification
- `POST /webhook` - Receive WhatsApp messages

**WebSocket:**
- `WS /ws/dashboard` - Real-time case updates

### 🎨 Frontend Services

#### 1. **Next.js Frontend**
- **Status**: ✅ Configured with axios for API calls
- **Port**: `http://localhost:3000` (default)
- **API Client**: `frontend/src/lib/api.ts`
- **Location**: `frontend/`

#### 2. **API Client (Axios)**
- **Base URL**: `http://localhost:8000` (configurable via `NEXT_PUBLIC_API_URL`)
- **Timeout**: 30 seconds
- **Interceptors**: Request/response logging and error handling
- **Functions**:
  - `sendMessage()` - Send message to backend
  - `getCaseState()` - Retrieve case by ID
  - `healthCheck()` - Check backend connection
  - `getAllCases()` - List all cases

### 📋 How to Run

#### Backend:
```powershell
cd C:\Users\lenovo\Desktop\pvv\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend:
```powershell
cd C:\Users\lenovo\Desktop\pvv\frontend
npm install  # Install axios if not already installed
npm run dev
```

### 🔍 Connection Verification

1. **Backend Health Check:**
   ```powershell
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"ok","service":"PV Connect Backend"}`

2. **Frontend Connection:**
   - Open browser console
   - Look for `[API]` logs when sending messages
   - Check connection status in chat header (✓ Online / ⚠ Backend Offline)

3. **MongoDB Connection:**
   - Check backend logs on startup
   - Should see: `✓ MongoDB connected successfully`
   - If not, verify MongoDB is running and `.env` has correct `MONGODB_URI`

### 🐛 Troubleshooting

#### Backend not connecting:
- ✅ Check MongoDB is running: `mongod` or MongoDB Compass
- ✅ Verify `.env` file exists in root directory
- ✅ Check `MONGODB_URI` in `.env` matches your MongoDB instance
- ✅ Check backend logs for connection errors

#### Frontend can't reach backend:
- ✅ Verify backend is running on port 8000
- ✅ Check CORS settings in `backend/app/main.py`
- ✅ Verify `NEXT_PUBLIC_API_URL` in frontend (defaults to `http://localhost:8000`)
- ✅ Check browser console for CORS errors

#### Axios errors:
- ✅ Run `npm install` in frontend directory
- ✅ Check `frontend/package.json` includes `axios`
- ✅ Verify network tab in browser DevTools

### 📊 Data Flow

```
Frontend (React/Next.js)
    ↓ axios POST /api/test/message
Backend (FastAPI)
    ↓ LangGraph workflow
MongoDB (via motor)
    ↓ Save case/message
Response → Frontend
```

### 🔐 Environment Variables

**Backend** (`.env` in root):
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DATABASE` - Database name (default: `pv_connect`)
- `GEMINI_API_KEY` - Google Gemini API key
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name (optional)
- `CLOUDINARY_API_KEY` - Cloudinary API key (optional)
- `CLOUDINARY_API_SECRET` - Cloudinary API secret (optional)

**Frontend** (`.env.local` or environment):
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)

### ✅ All Systems Connected!

- ✅ MongoDB ↔ Backend (via motor)
- ✅ Backend ↔ Frontend (via axios)
- ✅ LangGraph workflow integrated
- ✅ All API endpoints working
- ✅ Error handling configured
- ✅ Connection status monitoring
