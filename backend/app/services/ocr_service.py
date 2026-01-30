import os
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()  # 🔴 THIS LINE IS IMPORTANT

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash"
)


import json
import re

def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from image bytes using Gemini Pro Vision.
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
        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": file_bytes
                }
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
