"""
FastAPI application for NOVA Pharmacovigilance Assistant
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.services.mongodb_service import mongodb_service
from app.graph import graph_app
from app.state import create_initial_state
from app.schemas.message_schemas import MessageInput, MessageOutput, StateResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    logger.info("Starting NOVA Pharmacovigilance Assistant...")
    await mongodb_service.connect()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await mongodb_service.disconnect()
    logger.info("Application shut down successfully")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LangGraph-powered pharmacovigilance assistant for adverse drug event reporting",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.post("/api/message", response_model=MessageOutput)
async def process_message(message_input: MessageInput):
    """
    Process incoming message and return response
    
    This is the main endpoint for conversational interaction
    """
    try:
        logger.info(f"Processing message from {message_input.sender_phone}")
        
        # Check if continuing existing case
        if message_input.case_id:
            # Retrieve existing state
            case = await mongodb_service.get_case(message_input.case_id)
            if not case:
                raise HTTPException(status_code=404, detail="Case not found")
            
            # Convert to NovaState
            state = dict(case)
            state["messages"].append({
                "role": "user",
                "content": message_input.message or "",
                "timestamp": ""
            })
        else:
            # Create new state
            state = create_initial_state(
                sender_phone=message_input.sender_phone,
                initial_message=message_input.message or ""
            )
        
        # Run graph
        result = await graph_app.ainvoke(state)
        
        # Extract response
        last_assistant_message = None
        for msg in reversed(result.get("messages", [])):
            if msg["role"] == "assistant":
                last_assistant_message = msg["content"]
                break
        
        if not last_assistant_message:
            last_assistant_message = "Thank you for your report. We're processing your information."
        
        return MessageOutput(
            response=last_assistant_message,
            case_id=result.get("case_id"),  # Can be None
            next_action=result.get("next_action"),
            status=result.get("status", "open")
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload", response_model=MessageOutput)
async def upload_document(
    file: UploadFile = File(...),
    case_id: str = Form(None),
    sender_phone: str = Form(None)
):
    """
    Handle document upload (prescription/bill)
    Trigger OCR extraction node in the graph
    """
    try:
        logger.info(f"Processing upload for case: {case_id}, phone: {sender_phone}")
        
        # Read file as bytes
        contents = await file.read()
        
        # Try upload to Cloudinary (optional - don't fail if it doesn't work)
        image_url = None
        try:
            from app.services.cloudinary_service import cloudinary_service
            image_url = await cloudinary_service.upload_image(
                contents, 
                file.filename or "prescription.jpg",
                folder="nova/prescriptions"
            )
            logger.info(f"Image uploaded to Cloudinary: {image_url}")
        except Exception as cloud_error:
            logger.warning(f"Cloudinary upload failed (continuing anyway): {cloud_error}")
        
        # Update State with BYTES (not base64 string)
        state_update = {
            "pending_image_data": contents,  # Store as bytes, not base64
            "pending_image_mime_type": file.content_type or "image/jpeg",
            "pending_image_url": image_url
        }
        
        if case_id:
             case = await mongodb_service.get_case(case_id)
             if not case:
                 raise HTTPException(status_code=404, detail="Case not found")
             state = dict(case)
             state.update(state_update)
             # Reset current node to extraction
             state["current_node"] = "document_extraction"
        else:
             # creating new case from upload
             if not sender_phone:
                 raise HTTPException(status_code=400, detail="sender_phone is required for new uploads")
             
             state = create_initial_state(sender_phone, "")
             state.update(state_update)
             state["current_node"] = "document_extraction"

        # Run graph
        result = await graph_app.ainvoke(state)
        
        # Extract response
        last_assistant_message = None
        for msg in reversed(result.get("messages", [])):
            if msg["role"] == "assistant":
                last_assistant_message = msg["content"]
                break

        if not last_assistant_message:
            last_assistant_message = "Document processed."

        return MessageOutput(
            response=last_assistant_message,
            case_id=result.get("case_id"),  # Can be None
            next_action=result.get("next_action"),
            status=result.get("status", "open")
        )

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/state/{case_id}", response_model=StateResponse)
async def get_case_state(case_id: str):
    """
    Retrieve full state for a case
    
    Useful for debugging and testing
    """
    try:
        case = await mongodb_service.get_case(case_id)
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return StateResponse(
            case_id=case.get("case_id", ""),
            sender_type=case.get("sender_type"),
            language=case.get("language"),
            extracted_data=case.get("extracted_data", {}),
            completeness_score=case.get("completeness_score", 0.0),
            confidence_score=case.get("confidence_score", 0.0),
            status=case.get("status", "open"),
            messages=case.get("messages", []),
            current_node=case.get("current_node")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test/patient")
async def test_patient_flow(message: str = "I took aspirin and got a rash"):
    """
    Test endpoint for patient flow
    
    Simulates a patient reporting an adverse event
    """
    try:
        message_input = MessageInput(
            message=message,
            sender_phone="+1234567890",
            case_id=None
        )
        
        result = await process_message(message_input)
        return result
        
    except Exception as e:
        logger.error(f"Error in test patient flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test/doctor")
async def test_doctor_flow(
    message: str = "Reporting ADR: Patient on metformin 500mg BID developed hypoglycemia"
):
    """
    Test endpoint for doctor flow
    
    Simulates a doctor reporting an adverse event
    """
    try:
        message_input = MessageInput(
            message=message,
            sender_phone="+1987654321",
            case_id=None
        )
        
        result = await process_message(message_input)
        return result
        
    except Exception as e:
        logger.error(f"Error in test doctor flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NOVA Pharmacovigilance Assistant API",
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "/health",
            "process_message": "/api/message",
            "get_state": "/api/state/{case_id}",
            "test_patient": "/api/test/patient",
            "test_doctor": "/api/test/doctor"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
