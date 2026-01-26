import httpx
from datetime import datetime
from typing import Optional

from app.services.cloudinary_service import upload_bytes
from app.services.ollama_service import get_model
from app.agents.nodes.nlp_extraction import extract_data_node
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def download_audio_from_url(url: str) -> Optional[bytes]:
    """Download audio from URL (for testing without WhatsApp)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        return None


async def process_voice_node(state: GraphState) -> GraphState:
    """
    Handles voice notes using Ollama:
    1) Get audio bytes (from media_url or direct upload)
    2) Upload to Cloudinary (optional)
    3) Transcribe with external service (Ollama doesn't support audio directly)
    4) Run same extraction pipeline on transcript
    
    Note: Ollama doesn't natively support audio transcription. 
    You may need to use Whisper API or another transcription service.
    For now, this will log a warning and skip transcription.
    """
    audio_bytes: Optional[bytes] = None
    media_url = state.get("media_url")
    
    # Get audio bytes
    if media_url:
        audio_bytes = await download_audio_from_url(media_url)
    elif state.get("audio_bytes"):
        audio_bytes = state.get("audio_bytes")
    
    if not audio_bytes:
        logger.warning("No audio data provided to voice processing node")
        return state
    
    # Upload to Cloudinary (optional)
    cloudinary_url = None
    public_id = None
    try:
        upload_result = upload_bytes(
            audio_bytes, 
            folder=f"voice/{state.get('case_id', 'unknown')}", 
            resource_type="video"
        )
        cloudinary_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
    except Exception as e:
        logger.warning(f"Cloudinary upload failed (continuing without it): {e}")
    
    # Transcribe audio - Ollama doesn't support audio directly
    # TODO: Integrate Whisper API or another transcription service
    transcript = ""
    logger.warning("Audio transcription not yet implemented with Ollama. "
                   "Consider using Whisper API or another transcription service.")
    
    # Placeholder: In a real implementation, you would call a transcription service here
    # For example:
    # from app.services.whisper_service import transcribe_audio
    # transcript = await transcribe_audio(audio_bytes)
    
    # Save voice note metadata
    state.setdefault("voice_notes", [])
    state["voice_notes"].append({
        "cloudinary_url": cloudinary_url,
        "cloudinary_public_id": public_id,
        "transcript": transcript,
        "uploaded_at": datetime.utcnow().isoformat(),
    })
    
    # Process transcript as text message
    if transcript:
        state["message"] = transcript
        # Run NLP extraction on transcript
        state = await extract_data_node(state)
    else:
        logger.warning("Empty transcript - skipping NLP extraction")
    
    return state
