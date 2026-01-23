import google.generativeai as genai
import json
from typing import Dict, Any, Optional
from app.config import GEMINI_API_KEY
from app.prompts import PATIENT_WORKFLOW_PROMPT, DOCTOR_WORKFLOW_PROMPT, SYSTEM_CONTEXT_PROMPT
import logging

logger = logging.getLogger(__name__)

# Configure once
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not configured")


def get_model(name: str = "gemini-2.5-flash"):
    """Get Gemini model instance"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    return genai.GenerativeModel(name)


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


async def detect_language(message: str) -> Dict[str, str]:
    """Detect language from message text"""
    try:
        model = get_model()
        prompt = f'''{SYSTEM_CONTEXT_PROMPT}

Detect the language of this message and return ONLY the ISO 639-1 language code.
If uncertain, return "en".

Message: {message}

Return format: {{"language": "en"}}'''
        
        response = model.generate_content(prompt)
        text = clean_json_text(response.text)
        result = json.loads(text)
        return {"language": result.get("language", "en")}
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return {"language": "en"}


async def extract_adverse_event(message: str) -> Dict[str, Any]:
    """Extract adverse event data from free text"""
    try:
        model = get_model()
        # Using Patient Workflow Prompt Step 1
        prompt = f'''{PATIENT_WORKFLOW_PROMPT}

### INPUT MESSAGE
"{message}"

### INSTRUCTION
Execute STEP 1: Extract ONLY the fields drug_name, symptoms, severity, start_date, dosage.
Return JSON only.'''
        
        response = model.generate_content(prompt)
        text = clean_json_text(response.text)
        result = json.loads(text)
        return result
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return {}


async def detect_user_type_from_message(message: str) -> str:
    """Analyze message to detect if sender is medical professional"""
    try:
        model = get_model()
        # Using Doctor Workflow Prompt Step 1
        prompt = f'''{DOCTOR_WORKFLOW_PROMPT}

### MESSAGE TO ANALYZE
"{message}"

### INSTRUCTION
Execute STEP 1: Is this message indicating doctor intent?
Return JSON: {{"is_doctor": true|false}}'''
        
        response = model.generate_content(prompt)
        text = clean_json_text(response.text)
        result = json.loads(text)
        return "doctor" if result.get("is_doctor") else "patient"
    except Exception as e:
        logger.error(f"User type detection error: {e}")
        return "patient"  # Default to patient (safer)


async def triage_case(extracted_data: Dict[str, Any], known_effects: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Clinical triage - categorize risk level"""
    try:
        model = get_model()
        
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
        
        response = model.generate_content(prompt)
        text = clean_json_text(response.text)
        result = json.loads(text)
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
        model = get_model()
        
        # Using Patient Workflow Prompt Step 4
        prompt = f'''{PATIENT_WORKFLOW_PROMPT}

### CURRENT STATUS
- Missing field: {field}
- Patient language: {language}
- Existing data: {context}

### INSTRUCTION
Execute STEP 4: Generate ONLY ONE follow-up question for the missing field "{field}".
Return ONLY the question text string. No JSON.'''
        
        response = model.generate_content(prompt)
        question = response.text.strip().strip('"').strip("'")
        return question
    except Exception as e:
        logger.error(f"Follow-up generation error: {e}")
        return f"Can you provide more information about {field}?"
