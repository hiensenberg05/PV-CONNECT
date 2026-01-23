import io
import json
import httpx
from datetime import datetime
from typing import Any, Optional
from PIL import Image

from app.services.cloudinary_service import upload_bytes
from app.services.gemini_service import get_model
from app.services.mongodb_service import search_drugs
from app.agents.state import GraphState
import logging

logger = logging.getLogger(__name__)


async def download_image_from_url(url: str) -> Optional[bytes]:
    """Download image from URL (for testing without WhatsApp)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None


async def process_image_node(state: GraphState) -> GraphState:
    """
    Handles prescription / document uploads using Gemini 2.0 Flash Vision:
    1) Get image bytes (from media_url or direct upload)
    2) Upload to Cloudinary (optional)
    3) Run Gemini 2.0 Flash Vision to extract drug/dosage/frequency/doctor/clinic
    4) Validate drug name against MongoDB drugs_database for confidence
    """
    image_bytes: Optional[bytes] = None
    media_url = state.get("media_url")
    
    # Get image bytes
    if media_url:
        # Download from URL (for testing or WhatsApp media)
        image_bytes = await download_image_from_url(media_url)
    elif state.get("image_bytes"):
        # Direct bytes (for testing)
        image_bytes = state.get("image_bytes")
    
    if not image_bytes:
        logger.warning("No image data provided to OCR node")
        return state
    
    # Upload to Cloudinary (optional - can skip if not configured)
    cloudinary_url = None
    public_id = None
    try:
        upload_result = upload_bytes(
            image_bytes, 
            folder=f"prescriptions/{state.get('case_id', 'unknown')}"
        )
        cloudinary_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
    except Exception as e:
        logger.warning(f"Cloudinary upload failed (continuing without it): {e}")
    
    # Use Gemini 2.0 Flash for OCR (supports vision)
    try:
        model = get_model("gemini-2.0-flash")  # Gemini 2.0 Flash supports vision
        
        prompt = """Extract structured data from this prescription image.
Return ONLY valid JSON with these keys:
- drug_name: string or null
- dosage: string or null  
- frequency: string or null
- doctor_name: string or null
- clinic_name: string or null

Rules:
- Extract ONLY what is clearly visible
- Use null for unreadable or missing fields
- Return valid JSON only, no markdown, no code blocks"""
        
        # Open image and process with Gemini Vision
        image = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt, image])
        
        # Parse JSON response
        response_text = response.text.strip() if hasattr(response, 'text') else str(response).strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            parts = response_text.split("```")
            if len(parts) > 1:
                response_text = parts[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
        
        ocr_data = json.loads(response_text)
        logger.info(f"OCR extracted: {list(ocr_data.keys())}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OCR JSON: {e}, response: {response.text[:200]}")
        ocr_data = {}
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        ocr_data = {}
    
    # Validate drug name against database
    drug_name = ocr_data.get("drug_name") if isinstance(ocr_data, dict) else None
    confidence = 0.5  # Default confidence
    
    if drug_name:
        try:
            drug_profile = await search_drugs(drug_name)
            confidence = 0.9 if drug_profile else 0.6
        except Exception as e:
            logger.warning(f"Drug validation error: {e}")
    
    # Save document metadata
    state.setdefault("documents", [])
    state["documents"].append({
        "type": "prescription",
        "cloudinary_url": cloudinary_url,
        "cloudinary_public_id": public_id,
        "ocr_data": ocr_data,
        "ocr_confidence": confidence,
        "uploaded_at": datetime.utcnow().isoformat(),
    })
    
    # Merge OCR data into extracted_data
    if isinstance(ocr_data, dict):
        existing_data = state.get("extracted_data", {})
        for key in ["drug_name", "dosage", "frequency"]:
            value = ocr_data.get(key)
            if value:  # Only update non-null values
                existing_data[key] = value
        state["extracted_data"] = existing_data
    
    return state
