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
        import asyncio
        from app.services.mongodb_service import get_db, MONGODB_AVAILABLE
        if not MONGODB_AVAILABLE:
            logger.warning("⚠ MongoDB (motor) not available - running in test mode")
        else:
            db = await get_db()
            if db is None:
                logger.warning("⚠ MongoDB not available - running in test mode")
            else:
                # Test connection with ping
                # Don't block startup if Mongo isn't running.
                await asyncio.wait_for(db.command("ping"), timeout=2.0)
                logger.info("✓ MongoDB connected successfully")
                logger.info("✓ MongoDB ping successful")
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
    
    # Verify Ollama connection
    from app.config import OLLAMA_BASE_URL
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL or 'http://localhost:11434'}/api/tags")
            if response.status_code == 200:
                logger.info(f"✓ Ollama connected at {OLLAMA_BASE_URL or 'http://localhost:11434'}")
            else:
                logger.warning(f"⚠ Ollama responded with status {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠ Ollama not available at {OLLAMA_BASE_URL or 'http://localhost:11434'}: {e}")
        logger.info("ℹ Make sure Ollama is running: ollama serve")
    
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
