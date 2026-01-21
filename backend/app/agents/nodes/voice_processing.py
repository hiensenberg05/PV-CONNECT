import json
from datetime import datetime

from app.services.cloudinary_service import upload_bytes
from app.services.gemini_service import get_model
from app.agents.nodes.nlp_extraction import extract_data_node
from app.agents.state import CaseState


async def process_voice_node(state: CaseState) -> CaseState:
    """
    Handles voice notes:
    1) download media (stub to be implemented with WhatsApp media API)
    2) upload to Cloudinary (resource_type=video)
    3) transcribe with Gemini STT
    4) run same extraction pipeline on transcript
    """
    audio_bytes: bytes = state.get("current_message_media", b"")
    upload = upload_bytes(audio_bytes, folder=f"voice/{state.get('case_id', 'unknown')}", resource_type="video")
    cloudinary_url = upload.get("secure_url")
    public_id = upload.get("public_id")

    model = get_model("gemini-2.0-flash-exp")
    response = model.generate_content(["Transcribe this audio. Return only transcript text.", audio_bytes])
    transcript = response.text.strip() if response and response.text else ""

    state.setdefault("voice_notes", [])
    state["voice_notes"].append(
        {
            "cloudinary_url": cloudinary_url,
            "cloudinary_public_id": public_id,
            "transcript": transcript,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
    )

    state["current_message"] = transcript
    state = await extract_data_node(state)
    return state
