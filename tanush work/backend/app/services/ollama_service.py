import httpx
import json
from typing import Dict, Any, Optional
from app.config import OLLAMA_BASE_URL
from app.prompts import PATIENT_WORKFLOW_PROMPT, DOCTOR_WORKFLOW_PROMPT, SYSTEM_CONTEXT_PROMPT
import logging

logger = logging.getLogger(__name__)

# Default Ollama configuration
DEFAULT_OLLAMA_URL = "http://localhost:11434"
# Use the concrete model tag you have pulled locally
# e.g. `ollama pull llama3:8b`
DEFAULT_MODEL = "llama3:8b"


async def call_ollama(prompt: str, model: str = None) -> str:
    """Call Ollama API with a prompt"""
    base_url = OLLAMA_BASE_URL or DEFAULT_OLLAMA_URL
    model_name = model or DEFAULT_MODEL
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            }
            # Hint Ollama to return strict JSON when the prompt requests it.
            # Ref: Ollama /api/generate supports `format: "json"`.
            if "Return JSON" in prompt or "Return format:" in prompt:
                payload["format"] = "json"

            response = await client.post(
                f"{base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except httpx.TimeoutException:
        logger.error(f"Ollama request timeout for model {model_name}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Ollama request error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling Ollama: {e}")
        raise


async def call_ollama_vision(prompt: str, image_base64: str, model: str = None) -> str:
    """Call Ollama API with vision capabilities (for OCR)"""
    base_url = OLLAMA_BASE_URL or DEFAULT_OLLAMA_URL
    # Use a vision-capable model (llama3.2-vision, llava, etc.)
    model_name = model or "llama3.2-vision"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    except httpx.TimeoutException:
        logger.error(f"Ollama vision request timeout for model {model_name}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Ollama vision request error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling Ollama vision: {e}")
        raise


def clean_json_text(text: str) -> str:
    """Clean JSON text by removing markdown formatting"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def _extract_first_json_object(text: str) -> str:
    """
    Best-effort extraction of the first JSON object/array from a model response.
    Handles cases where the model adds surrounding prose.
    """
    text = clean_json_text(text)
    # Fast path: already looks like JSON.
    if text.startswith("{") and text.endswith("}"):
        return text
    if text.startswith("[") and text.endswith("]"):
        return text

    # Find first JSON object.
    start_obj = text.find("{")
    end_obj = text.rfind("}")
    if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
        return text[start_obj : end_obj + 1].strip()

    # Find first JSON array.
    start_arr = text.find("[")
    end_arr = text.rfind("]")
    if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
        return text[start_arr : end_arr + 1].strip()

    return text


async def detect_language(message: str) -> Dict[str, str]:
    """Detect language from message text"""
    try:
        prompt = f'''{SYSTEM_CONTEXT_PROMPT}

Detect the language of this message and return ONLY the ISO 639-1 language code.
If uncertain, return "en".

Message: {message}

Return format: {{"language": "en"}}'''
        
        response_text = await call_ollama(prompt)
        result = json.loads(_extract_first_json_object(response_text))
        return {"language": result.get("language", "en")}
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return {"language": "en"}


async def extract_adverse_event(message: str) -> Dict[str, Any]:
    """Extract adverse event data from free text"""
    try:
        # Using Patient Workflow Prompt Step 1
        prompt = f'''{PATIENT_WORKFLOW_PROMPT}

### INPUT MESSAGE
"{message}"

### INSTRUCTION
Execute STEP 1: Extract ONLY the fields drug_name, symptoms, severity, start_date, dosage.
Return JSON only.'''
        
        response_text = await call_ollama(prompt)
        result = json.loads(_extract_first_json_object(response_text))
        return result
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return {}


async def detect_user_type_from_message(message: str) -> str:
    """Analyze message to detect if sender is medical professional"""
    try:
        # Using Doctor Workflow Prompt Step 1
        prompt = f'''{DOCTOR_WORKFLOW_PROMPT}

### MESSAGE TO ANALYZE
"{message}"

### INSTRUCTION
Execute STEP 1: Is this message indicating doctor intent?
Return JSON: {{"is_doctor": true|false}}'''
        
        response_text = await call_ollama(prompt)
        result = json.loads(_extract_first_json_object(response_text))
        return "doctor" if result.get("is_doctor") else "patient"
    except Exception as e:
        logger.error(f"User type detection error: {e}")
        return "patient"  # Default to patient (safer)


async def triage_case(extracted_data: Dict[str, Any], known_effects: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Clinical triage - categorize risk level"""
    try:
        symptoms = extracted_data.get("symptoms", [])
        severity = extracted_data.get("severity", "unknown")
        drug_name = extracted_data.get("drug_name", "unknown")
        
        known_effects_str = "None" if not known_effects else str(known_effects.get("known_side_effects", []))
        
        # Triage logic is specific, so we use a specialized prompt but include System Context
        prompt = f'''{SYSTEM_CONTEXT_PROMPT}

You are assisting clinical triage for adverse event reports.
This is NOT diagnosis - only risk categorization.

Patient reported:
- Symptoms: {symptoms}
- Severity: {severity}
- Drug: {drug_name}

Known side effects for this drug: {known_effects_str}

Categorize risk level as:
- "low": Known, mild side effects
- "medium": Known but moderate symptoms
- "high": Severe symptoms OR contradictory to known profile

Return JSON:
{{
  "risk_level": "low|medium|high",
  "reason": "Brief explanation",
  "requires_human_review": true|false
}}

RULES:
- High risk if: severe symptoms OR unknown drug-symptom combination
- Unknown drug ≠ automatic high risk
- Explain reasoning clearly'''
        
        response_text = await call_ollama(prompt)
        result = json.loads(_extract_first_json_object(response_text))
        return result
    except Exception as e:
        logger.error(f"Triage error: {e}")
        return {
            "risk_level": "medium",
            "reason": "Error in triage analysis",
            "requires_human_review": True
        }


async def generate_followup(field: str, language: str, context: Dict[str, Any]) -> str:
    """Generate a single follow-up question for missing field"""
    try:
        # Using Patient Workflow Prompt Step 4
        prompt = f'''{PATIENT_WORKFLOW_PROMPT}

### CURRENT STATUS
- Missing field: {field}
- Patient language: {language}
- Existing data: {context}

### INSTRUCTION
Execute STEP 4: Generate ONLY ONE follow-up question for the missing field "{field}".
Return ONLY the question text string. No JSON.'''
        
        response_text = await call_ollama(prompt)
        question = response_text.strip().strip('"').strip("'")
        return question
    except Exception as e:
        logger.error(f"Follow-up generation error: {e}")
        return f"Can you provide more information about {field}?"


# Compatibility function for nodes that call get_model()
def get_model(name: str = None):
    """Compatibility function - returns a mock object for backward compatibility"""
    import base64
    
    class MockModel:
        def __init__(self, model_name):
            self.model_name = model_name or DEFAULT_MODEL
        
        async def generate_content(self, content, **kwargs):
            """Mock generate_content that calls Ollama"""
            if isinstance(content, list):
                # Handle vision cases - content[0] is prompt, content[1] is PIL Image
                prompt = content[0] if isinstance(content[0], str) else str(content[0])
                
                # Check if second element is an image
                if len(content) > 1:
                    from PIL import Image
                    import io
                    
                    if isinstance(content[1], Image.Image):
                        # Convert PIL Image to base64
                        img_buffer = io.BytesIO()
                        content[1].save(img_buffer, format='PNG')
                        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                        response_text = await call_ollama_vision(prompt, img_base64)
                        return MockResponse(response_text)
                
                # Fallback for non-vision list content
                return MockResponse(await call_ollama(prompt))
            else:
                prompt = content if isinstance(content, str) else str(content)
                return MockResponse(await call_ollama(prompt))
    
    class MockResponse:
        def __init__(self, text):
            self.text = text
    
    return MockModel(name)
