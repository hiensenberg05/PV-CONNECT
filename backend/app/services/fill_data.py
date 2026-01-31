# backend/app/services/fill_data.py
"""
Service to extract data from text and fill missing fields.
Uses LLM for extraction.

FIXES (Structure Preserved):
1. Aggressive extraction from ALL missing fields (prevents loops)
2. Better JSON parsing with multiple fallback strategies
3. Relaxed validation - more permissive
4. Explicit field removal from missing list
5. Debug logging for transparency
"""

import json
import re
from typing import Dict, Any
from datetime import datetime, timedelta
from app.services.llm_service import get_model


def _normalize_date_expression(raw_text: str) -> str:
    """
    Convert Hindi/English relative dates to actual dates (DD-MM-YYYY).
    
    Handles:
    - "2 din pehle" → calculates date 2 days ago
    - "kal" → yesterday
    - "parso" → day before yesterday
    - "abhi"/"ab" → today
    - Already formatted dates → pass through
    
    Args:
        raw_text: Raw date string from user
        
    Returns:
        Normalized date in DD-MM-YYYY format or original if can't parse
    """
    if not raw_text or not isinstance(raw_text, str):
        return raw_text
    
    text = raw_text.strip().lower()
    today = datetime.now()
    
    # If it's just a single digit or number without context, return as-is (likely invalid)
    if text.isdigit() and len(text) <= 2:
        return raw_text  # Don't try to normalize bare numbers like "1"
    
    # Check if already in proper format (DD-MM-YYYY or DD/MM/YYYY)
    if re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', text):
        # Normalize separators to dash
        return text.replace('/', '-')
    
    # Relative date patterns
    try:
        # "X din pehle" / "X days ago"
        match = re.search(r'(\d+)\s*(?:din|day)[s]?\s*(?:pehle|ago|phele|phle)', text)
        if match:
            days = int(match.group(1))
            target_date = today - timedelta(days=days)
            return target_date.strftime('%d-%m-%Y')
        
        # "kal" = yesterday (but not "aaj kal" or within other phrases)
        if re.search(r'\bkal\b', text) and 'parso' not in text and 'aaj' not in text:
            target_date = today - timedelta(days=1)
            return target_date.strftime('%d-%m-%Y')
        
        # "parso" / "prso" = day before yesterday
        if 'parso' in text or 'prso' in text:
            target_date = today - timedelta(days=2)
            return target_date.strftime('%d-%m-%Y')
        
        # "abhi" / "ab" / "now" / "aaj" = today
        if text in ['abhi', 'ab', 'now', 'aaj', 'today']:
            return today.strftime('%d-%m-%Y')
        
        # "yesterday"
        if 'yesterday' in text:
            target_date = today - timedelta(days=1)
            return target_date.strftime('%d-%m-%Y')
        
    except Exception as e:
        print(f"[Date Normalization] Error parsing '{raw_text}': {e}")
    
    # Return original if can't parse
    return raw_text


# Date fields that need normalization
DATE_FIELDS = {
    "medicine_start_date",
    "medicine_stop_date",
    "side_effect_start_date",
    "side_effect_stop_date",
    "medicine_expiry_date"  # Usually already in MM/YY format
}


# Field validation rules - RELAXED for better extraction
FIELD_VALIDATORS = {
    "patient_age_value": lambda v: str(v).replace(" ", "").isdigit() and 0 < int(v) < 150,
    "patient_age_unit": lambda v: any(u in v.lower() for u in ["year", "month", "day", "saal", "mahine", "din", "yr"]),
    "patient_gender": lambda v: any(g in v.lower() for g in ["male", "female", "other", "m", "f", "aadmi", "aurat", "ladka", "ladki", "purush", "mahila", "mard", "boy", "girl"]),
    "medicine_quantity_taken": lambda v: any(c.isdigit() for c in v),  # Must contain at least one digit
}


FILL_MISSING_SYSTEM_PROMPT = (
    "You are an Expert Pharmacovigilance Information Extractor.\n\n"
    "Your goal is to extract structured medical data from user messages.\n"
    "The user may speak in English, Hindi, or Hinglish (Hindi written in English).\n\n"
    
    "CRITICAL EXTRACTION RULES:\n"
    "1. **ONLY extract fields from the {target_fields} list provided**\n"
    "2. **ACCURACY OVER COMPLETENESS**: If information is NOT explicitly stated, return null. DO NOT GUESS.\n"
    "3. **NAME VALIDATION**: 'mujhe', 'main', 'hum' are PRONOUNS, NOT NAMES. Only extract proper names.\n"
    "4. **GENDER**: Extract Male/Female/Other. Hindi: 'male'/'ladka'/'aadmi' = Male, 'female'/'ladki'/'aurat' = Female.\n"
    "5. **AGE**: Must be a NUMBER only. Extract '25' from '25 years old'.\n"
    "6. **AGE UNIT**: Extract 'years', 'months', or 'days'.\n\n"
    
    "HINDI/HINGLISH NEGATIVE PATTERNS (CRITICAL):\n"
    "If user says ANY of these, extract field as 'None' or 'no':\n"
    "- 'nahi hai', 'nahi tha', 'nahi hain', 'nahi hua', 'nahi pada'\n"
    "- 'kuch nahi', 'koi nahi'\n"
    "- 'I don't have', 'no', 'none', 'nothing'\n"
    "- For yes/no fields: 'nahi' alone → 'no'\n"
    "Examples:\n"
    "- User: 'nahi hai' → {\"past_disease_history\": \"None\"}\n"
    "- User: 'hospital nahi gaya' → {\"severity_hospitalized\": \"no\"}\n"
    "- User: 'koi nahi' → {\"<any optional field>\": \"None\"}\n\n"
    
    "FIELD INFERENCE RULES (CRITICAL):\n"
    "1. **self_medicated**: If user mentions 'doctor', 'doctor ne kaha', 'advised' → Extract 'no'\n"
    "2. **self_medicated**: If user says 'self suggested', 'khud se liya', 'self advised' → Extract 'yes'\n"
    "3. **medicine_advised_by**: \n"
    "   - If 'doctor' mentioned → Extract 'doctor'\n"
    "   - If 'self suggested', 'khud se', 'self advised' → Extract 'self'\n"
    "4. **side_effect_continuing**: \n"
    "   - 'abhi bhi hai', 'still happening', 'ho raha hai' → Extract 'yes'\n"
    "   - 'band ho gaya', 'stopped', 'nahi hai ab' → Extract 'no'\n"
    "5. **side_effect_stop_date**: If side_effect_continuing='yes', leave as null (don't extract)\n"
    "6. **SEVERITY FIELDS (CRITICAL)**:\n"
    "   - severity_hospitalized: 'hospital gaya'/'admitted' → 'yes', 'nahi gaya'/'home care' → 'no'\n"
    "   - severity_death: User is chatting → ALWAYS 'no' (don't even try to extract)\n"
    "   - severity_affected_daily_activity: 'dikkat aayi'/'couldn't work' → 'yes', 'normal tha' → 'no'\n"
    "   - severity_no_daily_activity_effect: Inverse of above\n\n"
    
    "MEDICAL TERMS:\n"
    "- Medicine names: 'dolo', 'paracetamol', 'pudanahara', 'goli', 'tablet'\n"
    "- Dosage form: 'tablet', 'syrup', 'capsule', 'injection'\n"
    "- Symptoms: 'bukhar' (fever), 'dard' (pain), 'ulti' (vomiting), 'rashes'\n\n"
    
    "DATE HANDLING:\n"
    "- Future dates (MM/YY like 12/26) → medicine_expiry_date\n"
    "- Past references ('2 din pehle', 'yesterday', 'kal') → medicine_start_date or side_effect_start_date\n"
    "- Specific dates (DD-MM-YYYY) → Match to context (start/stop/expiry)\n"
    "- DATE RANGES: 'prso se aaj tk' (from day before yesterday to today):\n"
    "  * Extract START: 'prso' → side_effect_start_date\n"
    "  * Extract STOP: 'aaj' → side_effect_stop_date\n"
    "  * IGNORE duration numbers like '1 din' - these are NOT dates\n\n"
    
    "Output format (STRICT):\n"
    "- Return ONLY a valid JSON object\n"
    "- Keys must EXACTLY match target field names\n"
    "- Values must be strings or null\n"
    "- For negative answers: use string 'None'\n"
    "- For yes/no fields: use string 'yes' or 'no'\n"
    "- If nothing extractable: return {}\n"
    "- NO markdown code blocks (no ```json)\n"
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
        
    # ALLOW 'None' as a valid value (indicates user explicitly said they don't have info)
    if value_str == "None":
        return True
    
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
        r'^null$|^n/a$',  # Explicit null values (but 'None' is allowed above)
    ]
    
    for pattern in garbage_patterns:
        if re.match(pattern, value_str.lower()):
            return False
    
    return True


def fill_data_remove_missing(state: dict) -> dict:
    """
    FIXED VERSION - Aggressive extraction without section restrictions.
    
    KEY CHANGES:
    1. Extracts from ALL missing fields (not just current section)
    2. Prevents loops where LLM asks for already-mentioned data
    3. Explicit field removal from missing list
    
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

    # KEY FIX: Extract from ALL missing fields to prevent loops
    # If user says "pudanahara", extract it even if not in current section
    target_missing = all_missing[:20]  # Limit to prevent token overflow

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
        
        # Skip if already collected (don't overwrite)
        if key in extracted_data and extracted_data[key] is not None:
            continue
        
        # Validate value
        if not _validate_extracted_value(key, value):
            continue
        
        # APPLY DATE NORMALIZATION for date fields
        if key in DATE_FIELDS:
            value = _normalize_date_expression(value)
            print(f"[Date Normalization] {key}: '{new_data[key]}' → '{value}'")
        
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