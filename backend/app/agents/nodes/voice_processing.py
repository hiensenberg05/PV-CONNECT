import httpx
from datetime import datetime
from typing import Optional

from app.services.cloudinary_service import upload_bytes
from app.services.gemini_service import get_model
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
    Handles voice notes using Gemini 2.0 Flash:
    1) Get audio bytes (from media_url or direct upload)
    2) Upload to Cloudinary (optional)
    3) Transcribe with Gemini 2.0 Flash (supports audio)
    4) Run same extraction pipeline on transcript
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
    
    # Transcribe with Gemini 2.0 Flash (supports audio)
    transcript = ""
    try:
        model = get_model("gemini-2.0-flash")  # Gemini 2.0 Flash supports audio
        
        # Upload file to Gemini for processing
        # Upload file to Gemini for processing
        import google.generativeai as genai
        import tempfile
        import os

        # Create temp file for upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name
        
        try:
            audio_file = genai.upload_file(path=temp_path, mime_type="audio/wav")
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        prompt = "Transcribe this audio. Return ONLY the transcript text, no formatting, no JSON."
        response = model.generate_content([prompt, audio_file])
        transcript = response.text.strip() if response and response.text else ""
        
        logger.info(f"Voice transcribed: {len(transcript)} characters")
        
    except Exception as e:
        logger.error(f"Voice transcription error: {e}")
        transcript = ""
    
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
