# import json
# from datetime import datetime

# from app.services.cloudinary_service import upload_bytes
# from app.services.gemini_service import get_model
# from app.agents.nodes.nlp_extraction import extract_data_node
# from app.agents.state import CaseState


# async def process_voice_node(state: CaseState) -> CaseState:
#     """
#     Handles voice notes:
#     1) download media (stub to be implemented with WhatsApp media API)
#     2) upload to Cloudinary (resource_type=video)
#     3) transcribe with Gemini STT
#     4) run same extraction pipeline on transcript
#     """
#     audio_bytes: bytes = state.get("current_message_media", b"")
#     upload = upload_bytes(audio_bytes, folder=f"voice/{state.get('case_id', 'unknown')}", resource_type="video")
#     cloudinary_url = upload.get("secure_url")
#     public_id = upload.get("public_id")

#     model = get_model("gemini-2.0-flash-exp")
#     response = model.generate_content(["Transcribe this audio. Return only transcript text.", audio_bytes])
#     transcript = response.text.strip() if response and response.text else ""

#     state.setdefault("voice_notes", [])
#     state["voice_notes"].append(
#         {
#             "cloudinary_url": cloudinary_url,
#             "cloudinary_public_id": public_id,
#             "transcript": transcript,
#             "uploaded_at": datetime.utcnow().isoformat(),
#         }
#     )

#     state["current_message"] = transcript
#     state = await extract_data_node(state)
#     return state




# import json
# from datetime import datetime

# from app.agents.state import CaseState
# from app.agents.nodes.nlp_extraction import extract_data_node
# from app.services.cloudinary_service import upload_bytes
# from app.channels.whatsapp_media_service import download_whatsapp_media
# from app.services.gemini_service import get_model


# async def process_voice_node(state: CaseState) -> CaseState:
#     """
#     Handles voice notes.

#     Flow:
#     1) Read WhatsApp audio media_id from state["voice_notes_id"]
#     2) Download audio bytes from WhatsApp
#     3) Upload audio to Cloudinary (resource_type=video)
#     4) Transcribe audio to text
#     5) Run text extraction on transcript
#     6) Store voice metadata + transcript
#     """

#     voice_ids = state.get("voice_notes_id", [])
#     if not voice_ids:
#         return state

#     # ✅ Always process latest voice note
#     media_id = voice_ids[-1]

#     # 1️⃣ Download audio bytes (TEMPORARY, in-memory)
#     audio_bytes = await download_whatsapp_media(media_id)
#     if not audio_bytes:
#         return state

#     # 2️⃣ Upload to Cloudinary (PERMANENT)
#     upload = upload_bytes(
#         audio_bytes,
#         folder=f"voice/{state.get('case_id', 'unknown')}",
#         resource_type="video",
#     )

#     cloudinary_url = upload.get("secure_url")
#     public_id = upload.get("public_id")

#     # 3️⃣ Transcribe audio
#     model = get_model()  # STT-capable backend via abstraction
#     response = model.generate_content(
#         ["Transcribe this audio. Return ONLY transcript text.", audio_bytes]
#     )

#     transcript = response.text.strip() if response and response.text else ""

#     # 4️⃣ Store voice note metadata
#     state.setdefault("voice_notes", [])
#     state["voice_notes"].append(
#         {
#             "whatsapp_media_id": media_id,
#             "cloudinary_url": cloudinary_url,
#             "cloudinary_public_id": public_id,
#             "transcript": transcript,
#             "uploaded_at": datetime.utcnow().isoformat(),
#         }
#     )

#     # 5️⃣ Run NLP extraction on transcript (SAFE)
#     if transcript:
#         original_message = state.get("current_message", "")
#         state["current_message"] = transcript

#         state = await extract_data_node(state)

#         # 🔒 Restore original message
#         state["current_message"] = original_message

#     return state



import json
from datetime import datetime

from app.agents.state import CaseState
from app.agents.nodes.nlp_extraction import extract_data_node
from app.services.cloudinary_service import upload_bytes
from app.channels.whatsapp_media_service import download_whatsapp_media
from app.services.gemini_service import get_model


async def process_voice_node(state: CaseState) -> CaseState:
    """
    Handles voice notes.

    Flow:
    1) Read WhatsApp audio media_id from state["voice_notes_id"] (string or list)
    2) Download audio bytes from WhatsApp
    3) Upload audio to Cloudinary (resource_type=video)
    4) Transcribe audio to text
    5) Run text extraction on transcript
    6) Store voice metadata + transcript
    """

    voice_notes_id = state.get("voice_notes_id")

    # ✅ Handle string OR list
    if not voice_notes_id:
        return state

    if isinstance(voice_notes_id, list):
        media_id = voice_notes_id[-1]   # latest
    else:
        media_id = voice_notes_id       # single string

    # 1️⃣ Download audio bytes (TEMPORARY, in-memory)
    audio_bytes = await download_whatsapp_media(media_id)
    if not audio_bytes:
        return state

    # 2️⃣ Upload to Cloudinary (PERMANENT)
    upload = upload_bytes(
        audio_bytes,
        folder=f"voice/{state.get('case_id', 'unknown')}",
        resource_type="video",
    )

    cloudinary_url = upload.get("secure_url")
    public_id = upload.get("public_id")

    # 3️⃣ Transcribe audio
    model = get_model("whisper-large-v3")  # STT-capable backend via abstraction
    response = model.generate_content(
        ["Transcribe this audio. Return ONLY transcript text.", audio_bytes]
    )

    transcript = response.text.strip() if response and response.text else ""

    # 4️⃣ Store voice note metadata
    state.setdefault("voice_notes", [])
    state["voice_notes"].append(
        {
            "whatsapp_media_id": media_id,
            "cloudinary_url": cloudinary_url,
            "cloudinary_public_id": public_id,
            "transcript": transcript,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
    )

    # 5️⃣ Run NLP extraction on transcript (SAFE)
    if transcript:
        original_message = state.get("current_message", "")
        state["current_message"] = transcript

        state = await extract_data_node(state)

        # 🔒 Restore original message
        state["current_message"] = original_message

        # ✅ expose voice-extracted data for compliance merge
        state["voice_extracted_data"] = state.get("extracted_data", {}).copy()

    return state

