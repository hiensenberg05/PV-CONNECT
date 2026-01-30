# backend/app/services/fill_data.py
"""
Service to extract data from text and fill missing fields.
Uses LLM for extraction.

FIXES:
1. Section-aware extraction (only extract from current section)
2. Better JSON parsing with multiple fallback strategies
3. Value validation before storing
4. Logging for debugging
5. Error handling improvements
"""

import json
import re
from typing import Dict, Any
from services.llm_service import get_model


# Field validation rules
FIELD_VALIDATORS = {
    "patient_age_value": lambda v: v.isdigit() and 0 < int(v) < 150,
    "patient_age_unit": lambda v: v.lower() in ["years", "months", "days", "year", "month", "day", "साल", "महीने", "दिन", "saal", "mahine", "din", "yrs"],
    "patient_gender": lambda v: any(g in v.lower() for g in ["male", "female", "other", "m", "f", "aadmi", "aurat", "ladka", "ladki", "purush", "mahila", "mard"]),
    "medicine_quantity_taken": lambda v: any(c.isdigit() for c in v),  # Must contain at least one digit
}


FILL_MISSING_SYSTEM_PROMPT = (
    "You are an Expert Pharmacovigilance Information Extractor.\n\n"
    "Your goal is to extract structured medical data from user messages.\n"
    "The user may speak in English, Hindi, or Hinglish (Hindi written in English).\n\n"
    
    "CRITICAL EXTRACTION RULES:\n"
    "1. **ONLY extract fields from the {target_fields} list provided**\n"
    "2. **ACCURACY OVER COMPLETENESS**: If information is NOT explicitly stated, return null. DO NOT GUESS.\n"
    "3. **NAME VALIDATION**: 'mujhe', 'main', 'hum' are PRONOUNS, NOT NAMES. Only extract proper names like 'Rahul', 'Priya'.\n"
    "4. **GENDER**: Only extract Male/Female/Other (or Hindi equivalents). 'Bukhar', 'Dard' are symptoms, NOT genders.\n"
    "5. **AGE**: Must be a NUMBER only. Extract '25' from '25 years old'.\n"
    "6. **AGE UNIT**: Extract 'years', 'months', or 'days' (or Hindi: 'साल', 'महीने', 'दिन').\n"
    "7. **DATES**: Format as DD-MM-YYYY or DD/MM/YYYY if possible.\n"
    "8. **BOOLEAN FIELDS**: Return 'yes'/'no' or 'true'/'false' for fields like 'self_medicated', 'side_effect_continuing'.\n"
    "9. **MEDICAL TERMS**: Understand Hinglish:\n"
    "   - 'Dawai', 'Goli', 'Tablet', 'Syrup' -> medicine_name\n"
    "   - 'Bawasir', 'Piles', 'Ulti', 'Vomiting' -> Symptoms/Side effects\n"
    "   - COMBINED DOSAGE: If user says '500mg 2 times', extract ALL of it as medicine_quantity_taken.\n"
    "   - DOSAGE FORM: If user says 'pill', 'tablet', 'capsule', extract as medicine_dosage_form. If implied (e.g. '500mg'), check if form is mentioned elsewhere.\n"
    "   - DATES: Extract 'MM/YYYY' (e.g. 05/2026) as expiry. Extract ranges '15-01-2025 to 20-01-2025' into start/stop dates.\n\n"
    
    "Output format (STRICT):\n"
    "- Return ONLY a valid JSON object\n"
    "- Keys must EXACTLY match the target field names\n"
    "- Values must be strings or null (never boolean true/false, use 'yes'/'no')\n"
    "- If nothing can be extracted, return: {}\n"
    "- DO NOT include markdown code blocks (no ```json)\n"
)


def _extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON from LLM response with multiple fallback strategies.
    
    Handles:
    - Markdown code blocks (```json ... ```)
    - Inline JSON
    - Malformed JSON with trailing commas
    """
    # Strategy 1: Remove markdown code blocks
    if "```" in text:
        # Find content between ``` markers
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
        else:
            # Remove all ``` markers
            text = re.sub(r'```(?:json)?', '', text)
    
    # Strategy 2: Find JSON object in text
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if match:
        text = match.group(0)
    
    # Strategy 3: Clean common JSON errors
    text = text.strip()
    # Remove trailing commas before closing braces
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try one more time with aggressive cleaning
        text = re.sub(r'//.*?\n', '', text)  # Remove comments
        text = re.sub(r',\s*}', '}', text)   # Remove trailing commas
        try:
            return json.loads(text)
        except:
            return {}


def _validate_extracted_value(field_name: str, value: Any) -> bool:
    """
    Validate extracted value against field-specific rules.
    
    Returns:
        True if valid, False if invalid (should not be stored)
    """
    if value is None or value == "":
        return False
    
    # Convert to string for validation
    value_str = str(value).strip()
    
    if not value_str:
        return False
    
    # Check field-specific validators
    if field_name in FIELD_VALIDATORS:
        try:
            return FIELD_VALIDATORS[field_name](value_str)
        except:
            return False
    
    # Generic validation: no garbage values
    garbage_patterns = [
        r'^[^a-zA-Z0-9\u0900-\u097F\s]+$',  # Only special characters
        r'^\s+$',  # Only whitespace
        r'^null$|^none$|^n/a$',  # Explicit null values
    ]
    
    for pattern in garbage_patterns:
        if re.match(pattern, value_str.lower()):
            return False
    
    return True


def fill_data_remove_missing(state: dict) -> dict:
    """
    IMPROVED version with:
    - Section-aware extraction
    - Better JSON parsing
    - Value validation
    - Error handling
    
    Args:
        state: Conversation state with:
            - to_use: Combined useful text
            - missing: List of ALL missing field names
            - extracted_data: Dict of already extracted data
            - current_section_index: Current section being collected (optional)

    Returns:
        Updated state with new extractions added to extracted_data
        and fields removed from missing.
    """
    to_use = state.get("to_use", "")
    all_missing = state.get("missing", [])
    extracted_data = state.get("extracted_data", {})

    # Nothing to do
    if not to_use or not all_missing:
        return state

    # CRITICAL FIX: Only extract from current section's missing fields
    # This prevents LLM from hallucinating data for future sections
    from schemas.conversation_state import SECTIONS_ORDER
    
    current_section_index = state.get("current_section_index", 0)
    
    # Determine target fields (Current Section + Next Section to capture spillover)
    if current_section_index < len(SECTIONS_ORDER):
        current_section_fields = SECTIONS_ORDER[current_section_index]
        target_missing = [f for f in current_section_fields if f in all_missing]
        
        # ALWAYS peek at the next section too, in case user provides data ahead of time
        if current_section_index + 1 < len(SECTIONS_ORDER):
            next_section_fields = SECTIONS_ORDER[current_section_index + 1]
            next_missing = [f for f in next_section_fields if f in all_missing]
            target_missing.extend(next_missing)
            
        # Limit total fields to avoid token overflow (e.g. keep top 10)
        target_missing = target_missing[:15]
    else:
        # Fallback: extract from all missing (shouldn't happen)
        target_missing = all_missing

    if not target_missing:
        return state

    client, model = get_model()

    # Improved prompt with section context
    messages = [
        {
            "role": "system",
            "content": FILL_MISSING_SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"ONLY extract these fields (ignore others):\n{', '.join(target_missing)}"
        },
        {
            "role": "system",
            "content": f"Already collected (for context only, DO NOT re-extract):\n{json.dumps(extracted_data, indent=2)}"
        },
        {
            "role": "user",
            "content": to_use
        }
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=500  # Limit to prevent excessive output
        )

        raw_output = response.choices[0].message.content.strip()
        
        # Parse JSON with improved extraction
        new_data = _extract_json_from_text(raw_output)
        
        if not new_data:
            # LLM returned nothing useful
            return state

    except Exception as e:
        # API error or parsing failure
        print(f"[fill_data] Error during extraction: {str(e)}")
        return state

    # Update extracted_data and remove from missing with validation
    fields_extracted = []
    
    for key, value in new_data.items():
        # CRITICAL: Only process fields that were requested
        if key not in target_missing:
            continue
        
        # Validate value
        if not _validate_extracted_value(key, value):
            continue
        
        # Store and remove from missing
        extracted_data[key] = value
        if key in all_missing:
            all_missing.remove(key)
            fields_extracted.append(key)

    # HEURISTIC: If age value collected but unit is missing, assume Years (if reasonable)
    if "patient_age_value" in extracted_data and "patient_age_unit" in all_missing:
        try:
            age_val = int(extracted_data["patient_age_value"])
            if age_val > 5:  # Assume years for anyone older than 5
                extracted_data["patient_age_unit"] = "Years"
                all_missing.remove("patient_age_unit")
                fields_extracted.append("patient_age_unit (Inferred)")
        except:
            pass

    state["extracted_data"] = extracted_data
    state["missing"] = all_missing
    
    # Optional: Log what was extracted for debugging
    if fields_extracted:
        print(f"[fill_data] Extracted: {', '.join(fields_extracted)}")

    return state