import io
import json
from datetime import datetime
from typing import Any

from PIL import Image

from app.services.cloudinary_service import upload_bytes
from app.services.gemini_service import get_model
from app.services.mongodb_service import get_db
from app.agents.state import CaseState


async def process_image_node(state: CaseState) -> CaseState:
    """
    Handles prescription / document uploads:
    1) download media (stub to be implemented with WhatsApp media API)
    2) upload to Cloudinary
    3) run Gemini Vision to extract drug/dosage/frequency/doctor/clinic
    4) validate drug name against MongoDB drugs_database for confidence
    """
    # TODO: replace with actual WhatsApp media download
    image_bytes: bytes = state.get("current_message_media", b"")
    upload = upload_bytes(image_bytes, folder=f"prescriptions/{state.get('case_id', 'unknown')}")
    cloudinary_url = upload.get("secure_url")
    public_id = upload.get("public_id")

    model = get_model("gemini-pro-vision")
    prompt = """
    Extract structured data from this prescription image.
    Return JSON with keys:
      drug_name, dosage, frequency, doctor_name, clinic_name
    Use null for missing fields.
    """
    response = model.generate_content([prompt, Image.open(io.BytesIO(image_bytes))])
    try:
        ocr_data: Any = json.loads(response.text)
    except Exception:
        ocr_data = {}

    db = get_db()
    drug = db.drugs_database.find_one({"name": {"$regex": f"^{ocr_data.get('drug_name','')}", "$options": "i"}}) if ocr_data else None
    confidence = 0.9 if drug else 0.5

    state.setdefault("documents", [])
    state["documents"].append(
        {
            "type": "prescription",
            "cloudinary_url": cloudinary_url,
            "cloudinary_public_id": public_id,
            "ocr_data": ocr_data,
            "ocr_confidence": confidence,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
    )

    for key in ["drug_name", "dosage", "frequency"]:
        value = ocr_data.get(key) if isinstance(ocr_data, dict) else None
        if value:
            state.setdefault("extracted_data", {})[key] = value
    return state
