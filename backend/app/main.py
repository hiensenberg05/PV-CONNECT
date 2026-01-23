from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import websockets
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(title="PV Connect", version="0.1.0")

# Allow dashboard dev origin; tighten in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Removed: webhooks (WhatsApp disabled), dashboard (not used)
app.include_router(websockets.router)

# Test endpoints for LangGraph (without WhatsApp)
from app.api import test_graph
app.include_router(test_graph.router, tags=["test"])  # No prefix - endpoints define their own paths


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "PV Connect Backend"}


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "PV Connect Backend",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "test_message": "/api/test/message",
            "test_case": "/api/test/case/{case_id}",
            "websocket": "/ws/dashboard"
        },
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("PV Connect Backend starting up...")
    
    # Initialize MongoDB connection
    try:
        from app.services.mongodb_service import get_db, MONGODB_AVAILABLE
        if not MONGODB_AVAILABLE:
            logger.warning("⚠ MongoDB (motor) not available - running in test mode")
        else:
            db = await get_db()
            if db is None:
                logger.warning("⚠ MongoDB not available - running in test mode")
            else:
                # Test connection with ping
                await db.command("ping")
                logger.info("✓ MongoDB connected successfully")
                logger.info("✓ MongoDB ping successful")
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
    
    # Verify Gemini API key
    from app.config import GEMINI_API_KEY
    if GEMINI_API_KEY:
        logger.info("✓ Gemini API key configured")
    else:
        logger.warning("⚠ Gemini API key not configured")
    
    # Verify Cloudinary (optional)
    from app.config import CLOUDINARY_CLOUD_NAME
    if CLOUDINARY_CLOUD_NAME:
        logger.info("✓ Cloudinary configured")
    else:
        logger.info("ℹ Cloudinary not configured (optional)")
    
    logger.info("✓ Backend initialization complete")
    print("\n🚀 Backend is running! Access it at: http://localhost:8000\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("PV Connect Backend shutting down...")
