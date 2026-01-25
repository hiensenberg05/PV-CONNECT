import json
from app.services.gemini_service import get_model
from app.agents.state import CaseState


async def consolidated_processor_node(state: CaseState) -> CaseState:
    """
    Consolidated node that performs language detection, user type detection,
    data extraction, and clinical triage in a single Gemini API call.
    
    This reduces API calls from 5-6 to just 1 per request.
    """
    model = get_model("gemini-2.0-flash-exp")
    text = state.get("current_message", "")
    
    prompt = f"""
You are a pharmacovigilance AI assistant. Analyze the following message and return a comprehensive JSON response.

MESSAGE: "{text}"

Return ONLY valid JSON with this exact structure:
{{
    "language": "ISO language code (e.g., 'en', 'hi', 'es')",
    "user_type": "patient or doctor",
    "extracted_data": {{
        "drug_name": "name of the drug or null",
        "symptoms": ["list", "of", "symptoms"] or [],
        "severity": "mild/moderate/severe or null",
        "start_date": "date or null",
        "dosage": "dosage information or null"
    }},
    "triage": {{
        "priority": "low/medium/high",
        "is_unusual": true or false,
        "reason": "brief explanation"
    }}
}}

Rules:
1. Detect the language from the message text
2. Classify if sender is a patient reporting symptoms or a doctor
3. Extract adverse event details (drug name, symptoms, severity, etc.)
4. Evaluate urgency and whether symptoms are unusual for the drug
5. Return ONLY the JSON, no additional text
"""
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        
        # Update state with all extracted information
        state["language"] = result.get("language", "en")[:2].lower()
        state["user_type"] = result.get("user_type", "patient").lower()
        
        # Merge extracted data
        extracted = result.get("extracted_data", {})
        state.setdefault("extracted_data", {})
        for key, value in extracted.items():
            if value:
                state["extracted_data"][key] = value
        
        # Store triage information
        state["triage"] = result.get("triage", {
            "priority": "medium",
            "is_unusual": False,
            "reason": "Default triage"
        })
        
    except json.JSONDecodeError:
        # Fallback to safe defaults if JSON parsing fails
        state["language"] = "en"
        state["user_type"] = "patient"
        state.setdefault("extracted_data", {})
        state["triage"] = {
            "priority": "medium",
            "is_unusual": False,
            "reason": "Failed to parse response"
        }
    except Exception as e:
        # Handle any other errors gracefully
        print(f"Error in consolidated processor: {e}")
        state["language"] = "en"
        state["user_type"] = "patient"
        state.setdefault("extracted_data", {})
        state["triage"] = {
            "priority": "medium",
            "is_unusual": False,
            "reason": f"Error: {str(e)}"
        }
    
    return state
