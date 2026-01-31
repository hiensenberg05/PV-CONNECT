# backend/app/main.py
"""
FastAPI Main Application - PV-CONNECT Backend
Provides REST API endpoints for frontend interaction.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from app.config import settings
from app.workflows.keep_workflow import process_message
from app.db.mongo_db import mongodb_service
from app.services.ocr_service import extract_text_from_image
from app.services.stt_service import transcribe_audio
from app.workflows.cache_store import get_state, clear_all_states
from app.api.webhooks import router as webhook_router
from app.api.auth import router as auth_router
from app.analytics.vigigrade import router as vigigrade_router
from app.api.medicines import router as medicines_router

# Configure logging with explicit format and handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Pharmacovigilance Data Collection Backend"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Pydantic Models for Request/Response
# ============================================

class MessageRequest(BaseModel):
    """Request model for sending a text message."""
    phone_number: str
    message: str


class MessageResponse(BaseModel):
    """Response model for message processing."""
    reply: str
    state: Optional[dict] = None
    success: bool = True


class StateResponse(BaseModel):
    """Response model for state retrieval."""
    state: Optional[dict] = None
    exists: bool


# ============================================
# Startup/Shutdown Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection and background tasks on startup."""
    import asyncio
    from app.services.inactivity_checker import run_inactivity_checker

    logger.info("Starting PV-CONNECT Backend...")
    await mongodb_service.connect()
    logger.info("✅ MongoDB connected successfully")

    # Start inactivity checker background task
    asyncio.create_task(run_inactivity_checker())
    logger.info("✅ Inactivity checker started")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    logger.info("Shutting down PV-CONNECT Backend...")
    await mongodb_service.disconnect()
    logger.info("✅ MongoDB disconnected")


# ============================================
# Health Check Endpoints
# ============================================

@app.get("/")
def root():
    """Root endpoint - health check."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "service": settings.APP_NAME
    }


# ============================================
# Message Processing Endpoints
# ============================================

@app.post("/api/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """
    Process a text message from the user.
    
    Args:
        request: MessageRequest with phone_number and message
        
    Returns:
        MessageResponse with bot reply and updated state
    """
    try:
        logger.info(f"Processing message from {request.phone_number}")
        
        result = await process_message(
            phone_number=request.phone_number,
            text_content=request.message
        )
        
        return MessageResponse(
            reply=result["reply"],
            state=result.get("state"),
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



from app.db.cloudinary_service import cloudinary_service

@app.post("/api/upload/image")
async def upload_image(
    phone_number: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and process an image (prescription, license, etc.).
    """
    try:
        logger.info(f"Processing image upload from {phone_number}")
        
        # Validate file type
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
            )
            
        # 1. Upload to Cloudinary
        image_url = await cloudinary_service.upload_file(
            file_bytes=file_content,
            filename=file.filename,
            folder="pv-connect/images"
        )
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image to storage")
        
        # 2. Extract text using OCR (using bytes in memory)
        ocr_text = extract_text_from_image(file_content)
        
        # 3. Process through workflow with Cloudinary URL
        result = await process_message(
            phone_number=phone_number,
            text_content=None,
            doc_id=image_url  # Use Cloudinary URL as doc_id
        )
        
        return {
            "reply": result["reply"],
            "ocr_text": ocr_text,
            "image_url": image_url,
            "state": result.get("state"),
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/audio")
async def upload_audio(
    phone_number: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and transcribe an audio message.
    """
    try:
        logger.info(f"Processing audio upload from {phone_number}")
        
        # Validate file type
        if file.content_type not in settings.ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {settings.ALLOWED_AUDIO_TYPES}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # 1. Upload to Cloudinary
        audio_url = await cloudinary_service.upload_file(
            file_bytes=file_content,
            filename=file.filename,
            folder="pv-connect/audio"
        )
        
        if not audio_url:
            raise HTTPException(status_code=500, detail="Failed to upload audio to storage")
            
        # 2. Transcribe audio (using bytes in memory)
        transcript = transcribe_audio(file_content)
        
        # 3. Process through workflow
        result = await process_message(
            phone_number=phone_number,
            text_content=transcript,
            voice_id=audio_url  # Use Cloudinary URL as voice_id
        )
        
        return {
            "reply": result["reply"],
            "transcript": transcript,
            "audio_url": audio_url,
            "state": result.get("state"),
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# State Management Endpoints
# ============================================

@app.get("/api/state/{phone_number}", response_model=StateResponse)
async def get_conversation_state(phone_number: str):
    """
    Retrieve the current conversation state for a user.
    
    Args:
        phone_number: User's phone number
        
    Returns:
        StateResponse with current state or None
    """
    try:
        state = get_state(phone_number)
        
        return StateResponse(
            state=state,
            exists=state is not None
        )
        
    except Exception as e:
        logger.error(f"Error retrieving state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/state/{phone_number}")
async def clear_conversation_state(phone_number: str):
    """
    Clear the conversation state for a user.
    
    Args:
        phone_number: User's phone number
        
    Returns:
        Success confirmation
    """
    try:
        from app.workflows.cache_store import delete_state
        
        deleted = delete_state(phone_number)
        
        return {
            "success": deleted,
            "message": "State cleared" if deleted else "No state found"
        }
        
    except Exception as e:
        logger.error(f"Error clearing state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/clear-all-states")
async def admin_clear_all_states():
    """
    Admin endpoint to clear all conversation states.
    WARNING: This will reset all active conversations.
    """
    try:
        clear_all_states()
        
        return {
            "success": True,
            "message": "All states cleared"
        }
        
    except Exception as e:
        logger.error(f"Error clearing all states: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cases")
async def get_all_cases():
    """
    Get all pharmacovigilance cases from the database.
    Used by the dashboard to display the case list.
    """
    try:
        cases_cursor = mongodb_service.db.cases.find().sort("updated_at", -1)
        cases = await cases_cursor.to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        results = []
        for case in cases:
            if "_id" in case:
                case["_id"] = str(case["_id"])
            results.append(case)
            
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Include Additional Routers
# ============================================

# WhatsApp webhook router (if using WhatsApp Business API)
app.include_router(webhook_router, tags=["webhooks"])

# Authentication router for employee login
app.include_router(auth_router)

# VigiGrade analytics router for confidence scoring and signal detection
app.include_router(vigigrade_router)

# Medicines database router
app.include_router(medicines_router)

# FAERS Analytics router
from app.api.analytics import router as analytics_router
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])


# ============================================
# Run Server (for development)
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
