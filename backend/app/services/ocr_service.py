import os
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()

# Initialize client with the new library
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

import json
import re

def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from image bytes using Google GenAI (Gemini).
    Returns the extracted text.
    """
    prompt = """
    Extract text from this medical document. 
    Identify:
    - document type (prescription, bill, license, irrelevant)
    - drug names
    - dosage
    - dates
    Respond in JSON only.
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
