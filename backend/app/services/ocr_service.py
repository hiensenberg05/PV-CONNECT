import os
from google import genai
from google.genai import types

# Import centralized settings (handles .env loading)
from app.config import settings

# Initialize client with the API key from settings
api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
client = genai.Client(api_key=api_key) if api_key else None

import json
import re

def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from image bytes using Google GenAI (Gemini).
    Returns the extracted text.
    """
    prompt = """
    You are a medical document OCR assistant for Pharmacovigilance.
    
    Extract ALL text and information from this medical document.
    
    Look for and extract:
    - Patient name
    - Patient age (number and unit like years/months)
    - Patient gender
    - Medicine/drug names
    - Dosage (quantity, form like tablet/syrup)
    - Dates (prescription date, medicine start/stop dates, expiry)
    - Doctor name
    - Hospital/clinic name
    - Any side effects or reactions mentioned
    - Reason for medicine / diagnosis
    
    Return as plain text in this format:
    Patient Name: [name if found]
    Age: [age if found]
    Gender: [gender if found]
    Medicine: [medicine name]
    Dosage: [dosage details]
    Dates: [any relevant dates]
    Additional Info: [any other relevant medical info]
    
    If a field is not visible or readable, skip it.
    Return ALL readable text from the document.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=file_bytes, mime_type="image/jpeg")
            ]
        )
        return response.text.strip()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

def run_ocr_on_state(state: dict, file_path: str) -> dict:
    """
    Legacy function for state-based processing from local file.
    """
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    extracted_text = extract_text_from_image(file_bytes)

    state["current_doc_data"] = {
        "raw_text": extracted_text,
        "entities": {
            "raw_ocr_text": extracted_text
        },
        "confidence": 0.85 if len(extracted_text) > 20 else 0.3
    }

    return state
