# import io
# import json
# from datetime import datetime
# from typing import Any

# from PIL import Image

# from app.services.cloudinary_service import upload_bytes
# from app.services.gemini_service import get_model
# from app.services.mongodb_service import get_db
# from app.agents.state import CaseState


# async def process_image_node(state: CaseState) -> CaseState:
#     """
#     Handles prescription / document uploads:
#     1) download media (stub to be implemented with WhatsApp media API)
#     2) upload to Cloudinary
#     3) run Gemini Vision to extract drug/dosage/frequency/doctor/clinic
#     4) validate drug name against MongoDB drugs_database for confidence
#     """
#     # TODO: replace with actual WhatsApp media download
#     image_bytes: bytes = state.get("current_message_media", b"")
#     upload = upload_bytes(image_bytes, folder=f"prescriptions/{state.get('case_id', 'unknown')}")
#     cloudinary_url = upload.get("secure_url")
#     public_id = upload.get("public_id")

#     model = get_model("gemini-pro-vision")
#     prompt = """
#     Extract structured data from this prescription image.
#     Return JSON with keys:
#       drug_name, dosage, frequency, doctor_name, clinic_name
#     Use null for missing fields.
#     """
#     response = model.generate_content([prompt, Image.open(io.BytesIO(image_bytes))])
#     try:
#         ocr_data: Any = json.loads(response.text)
#     except Exception:
#         ocr_data = {}

#     db = get_db()
#     drug = db.drugs_database.find_one({"name": {"$regex": f"^{ocr_data.get('drug_name','')}", "$options": "i"}}) if ocr_data else None
#     confidence = 0.9 if drug else 0.5

#     state.setdefault("documents", [])
#     state["documents"].append(
#         {
#             "type": "prescription",
#             "cloudinary_url": cloudinary_url,
#             "cloudinary_public_id": public_id,
#             "ocr_data": ocr_data,
#             "ocr_confidence": confidence,
#             "uploaded_at": datetime.utcnow().isoformat(),
#         }
#     )

#     for key in ["drug_name", "dosage", "frequency"]:
#         value = ocr_data.get(key) if isinstance(ocr_data, dict) else None
#         if value:
#             state.setdefault("extracted_data", {})[key] = value
#     return state



# import io
# import json
# from datetime import datetime
# from typing import Any

# from PIL import Image

# from app.agents.state import CaseState
# from app.services.cloudinary_service import upload_bytes
# from app.channels.whatsapp_media_service import download_whatsapp_media
# from app.services.gemini_service import get_model


# async def process_image_node(state: CaseState) -> CaseState:
#     """
#     Handles prescription / document uploads.

#     Uses:
#     - state["documents_id"] for WhatsApp media IDs
#     - Cloudinary for permanent storage
#     - OCR on raw bytes
#     """

#     document_ids = state.get("documents_id", [])
#     if not document_ids:
#         return state

#     # ✅ Always process the latest uploaded document
#     media_id = document_ids[-1]

#     # 1️⃣ Download image bytes from WhatsApp
#     image_bytes: bytes = await download_whatsapp_media(media_id)
#     if not image_bytes:
#         return state

#     # 2️⃣ Upload to Cloudinary
#     upload = upload_bytes(
#         image_bytes,
#         folder=f"prescriptions/{state.get('case_id', 'unknown')}"
#     )

#     cloudinary_url = upload.get("secure_url")
#     public_id = upload.get("public_id")

#     # 3️⃣ OCR extraction
#     model = get_model("vision")

#     prompt = """
# You are a medical OCR extraction system.

# Extract structured data from this prescription image.

# Return ONLY valid JSON.
# Do NOT add explanations.
# Do NOT wrap in markdown.

# JSON schema:
# {
#   "drug_name": string | null,
#   "dosage": string | null,
#   "frequency": string | null,
#   "doctor_name": string | null,
#   "clinic_name": string | null
# }
# """

#     try:
#         response = model.generate_content(
#             [prompt, Image.open(io.BytesIO(image_bytes))]
#         )
#         ocr_data: Any = json.loads(response.text)
#     except Exception:
#         ocr_data = {}

#     # 4️⃣ Save document metadata
#     state.setdefault("documents", [])
#     state["documents"].append(
#         {
#             "type": "prescription",
#             "whatsapp_media_id": media_id,
#             "cloudinary_url": cloudinary_url,
#             "cloudinary_public_id": public_id,
#             "ocr_data": ocr_data,
#             "uploaded_at": datetime.utcnow().isoformat(),
#         }
#     )

#     # 5️⃣ Merge OCR result into extracted_data (SAFE)
#     extracted = state.setdefault("extracted_data", {})
#     for key in ["drug_name", "dosage", "frequency"]:
#         if not extracted.get(key) and ocr_data.get(key):
#             extracted[key] = ocr_data[key]

#     return state



# import io
# import json
# from datetime import datetime
# from typing import Any

# from PIL import Image

# from app.agents.state import CaseState
# from app.services.cloudinary_service import upload_bytes
# from app.channels.whatsapp_media_service import download_whatsapp_media
# from app.services.gemini_service import get_model


# async def process_image_node(state: CaseState) -> CaseState:
#     """
#     Handles prescription / document uploads.

#     Uses:
#     - state["documents_id"] for WhatsApp media ID (string or list)
#     - Cloudinary for permanent storage
#     - OCR on raw bytes
#     """

#     documents_id = state.get("documents_id")

#     # ✅ Handle string OR list
#     if not documents_id:
#         return state

#     if isinstance(documents_id, list):
#         media_id = documents_id[-1]   # latest
#     else:
#         media_id = documents_id       # single string

#     # 1️⃣ Download image bytes from WhatsApp
#     image_bytes: bytes = await download_whatsapp_media(media_id)
#     if not image_bytes:
#         return state

#     # 2️⃣ Upload to Cloudinary
#     upload = upload_bytes(
#         image_bytes,
#         folder=f"prescriptions/{state.get('case_id', 'unknown')}"
#     )

#     cloudinary_url = upload.get("secure_url")
#     public_id = upload.get("public_id")

#     # 3️⃣ OCR extraction
#     model = get_model("vision")

#     prompt = """
#         You are a medical OCR extraction system.

#         Extract structured data from this prescription image.

#         Return ONLY valid JSON.
#         Do NOT add explanations.
#         Do NOT wrap in markdown.

#         JSON schema:
#         {
#         "drug_name": string | null,
#         "dosage": string | null,
#         "frequency": string | null,
#         "doctor_name": string | null,
#         "clinic_name": string | null
#         }
#         """

#     try:
#         response = model.generate_content(
#             [prompt, Image.open(io.BytesIO(image_bytes))]
#         )
#         ocr_data: Any = json.loads(response.text)
#     except Exception:
#         ocr_data = {}

#     # 4️⃣ Save document metadata
#     state.setdefault("documents", [])
#     state["documents"].append(
#         {
#             "type": "prescription",
#             "whatsapp_media_id": media_id,
#             "cloudinary_url": cloudinary_url,
#             "cloudinary_public_id": public_id,
#             "ocr_data": ocr_data,
#             "uploaded_at": datetime.utcnow().isoformat(),
#         }
#     )

#     # 5️⃣ Merge OCR result into extracted_data (SAFE)
#     extracted = state.setdefault("extracted_data", {})
#     for key in ["drug_name", "dosage", "frequency"]:
#         if ocr_data.get(key) not in (None, "", [], {}):
#             extracted[key] = ocr_data[key]

#     return state


import io
import json
from datetime import datetime
from typing import Any

from PIL import Image
import google.generativeai as genai

from app.agents.state import CaseState
from app.services.cloudinary_service import upload_bytes
from app.channels.whatsapp_media_service import download_whatsapp_media
from app.services.gemini_service import get_model   # Groq text model
from app.config import GEMINI_API_KEY


# Configure Gemini Vision
genai.configure(api_key=GEMINI_API_KEY)
vision_model = genai.GenerativeModel("gemini-1.5-flash")


async def process_image_node(state: CaseState) -> CaseState:
    """
    Handles prescription / document uploads.

    Uses:
    - state["documents_id"] for WhatsApp media ID (string or list)
    - Cloudinary for permanent storage
    - Gemini Vision for OCR
    - Groq LLM for structured extraction
    """

    documents_id = state.get("documents_id")

    # ✅ Handle string OR list
    if not documents_id:
        return state

    if isinstance(documents_id, list):
        media_id = documents_id[-1]
    else:
        media_id = documents_id

    # 1️⃣ Download image bytes from WhatsApp
    image_bytes: bytes = await download_whatsapp_media(media_id)
    if not image_bytes:
        return state

    # 2️⃣ Upload to Cloudinary
    upload = upload_bytes(
        image_bytes,
        folder=f"prescriptions/{state.get('case_id', 'unknown')}"
    )

    cloudinary_url = upload.get("secure_url")
    public_id = upload.get("public_id")

    # 3️⃣ OCR using Gemini Vision
    try:
        image = Image.open(io.BytesIO(image_bytes))

        ocr_response = vision_model.generate_content(
            [
                "Extract ALL readable text from this medical prescription. "
                "Return ONLY the text.",
                image,
            ]
        )

        ocr_text = ocr_response.text.strip() if ocr_response and ocr_response.text else ""
    except Exception:
        ocr_text = ""

    # 4️⃣ Structured extraction using Groq (text-only)
    if not ocr_text:
        ocr_data: Any = {}
    else:
        model = get_model()

        prompt = f"""
        You are a medical information extraction system.

        Extract structured data from this prescription text:

        {ocr_text}

        Return ONLY valid JSON.
        Do NOT add explanations.
        Do NOT wrap in markdown.

        JSON schema:
        {{
        "drug_name": string | null,
        "dosage": string | null,
        "frequency": string | null,
        "doctor_name": string | null,
        "clinic_name": string | null
        }}
        """

        try:
            response = model.generate_content(prompt)
            ocr_data = json.loads(response.text)
        except Exception:
            ocr_data = {}

    # 5️⃣ Save document metadata
    state.setdefault("documents", [])
    state["documents"].append(
        {
            "type": "prescription",
            "whatsapp_media_id": media_id,
            "cloudinary_url": cloudinary_url,
            "cloudinary_public_id": public_id,
            "ocr_data": ocr_data,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
    )

    # 6️⃣ Merge OCR result into extracted_data (SAFE)
    extracted = state.setdefault("extracted_data", {})
    for key in ["drug_name", "dosage", "frequency"]:
        if ocr_data.get(key) not in (None, "", [], {}):
            extracted[key] = ocr_data[key]

    return state
