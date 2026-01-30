# backend/app/services/see_useless.py
"""
Service to check if text input is useful for filling missing fields.
Uses LLM to make the determination.
"""

from app.services.llm_service import get_model


SEE_USELESS_SYSTEM_PROMPT = (
    "You are a Pharmacovigilance Information Validator.\n\n"
    "Your task: Determine if user input contains ANY useful medical/clinical information.\n"
    "The user may speak in English, Hindi, or Hinglish (Hindi written in English).\n\n"
    
    "CRITICAL BIAS: **When in doubt, mark as USEFUL (output NO)**\n"
    "It's better to pass questionable input to extraction than to reject valid medical info.\n\n"
    
    "HINGLISH MEDICAL VOCABULARY:\n"
    "- Conditions: 'Bhawasir/Bawaseer/Piles', 'Bukhar/Fever', 'Dard/Pain', 'Ulti/Vomiting', 'Khujli/Itching'\n"
    "- Medicines: 'Dawai/Dawa/Diwai', 'Goli', 'Tablet', 'Syrup', 'Injection'\n"
    "- Self-medication: 'Apne aap li', 'Khud se li', 'Bina doctor ke'\n"
    "- Prescribed: 'Doctor ne di', 'Doctor ne bola', 'Chemist ne diya'\n"
    "- Names: Any proper name like 'Rahul', 'Priya', 'Suresh', 'Amit'\n"
    "- Age: Numbers + 'saal/year/years/mahine/months', e.g., '25 saal', '30 years', '6 mahine'\n"
    "- Gender: 'Ladka/Boy/Male', 'Ladki/Girl/Female', 'Aadmi/Man', 'Aurat/Woman'\n"
    "- Dates: Any date format, 'kal', 'parso', '2 din pehle', 'last week'\n"
    "- Quantities: '1 tablet', '2 goli', 'do baar', 'twice daily'\n\n"
    
    "EXAMPLES OF USEFUL INPUT (output NO):\n"
    "- 'mera naam Rahul hai' → Contains name → NO\n"
    "- '25 saal ka hun' → Contains age → NO\n"
    "- 'bhawasir ki problem thi' → Contains medical condition → NO\n"
    "- 'dawai li thi' → Contains medicine reference → NO\n"
    "- 'male' → Contains gender → NO\n"
    "- 'years' → Contains age unit → NO\n"
    "- 'khud se li thi' → Contains self-medication info → NO\n"
    "- 'paracetamol' → Contains medicine name → NO\n"
    "- 'kal se shuru hui' → Contains date/timeline → NO\n\n"
    
    "EXAMPLES OF USELESS INPUT (output YES):\n"
    "- 'ok' → No medical info → YES\n"
    "- 'haan' → Just acknowledgment → YES\n"
    "- 'theek hai' → Just agreement → YES\n"
    "- Random emojis only → YES\n"
    "- 'hello' → Just greeting → YES\n\n"
    
    "DECISION RULES:\n"
    "1. Does the text contain ANY name, number, medical term, or clinical detail? → Output NO (useful)\n"
    "2. Is it ONLY a greeting, acknowledgment, or random text? → Output YES (useless)\n"
    "3. **DEFAULT: When uncertain, output NO** (pass to extraction for safety)\n\n"
    
    "OUTPUT FORMAT:\n"
    "- Output ONLY: YES or NO\n"
    "- YES = useless (no medical info)\n"
    "- NO = useful (contains medical info)\n"
    "- No explanations, no JSON, no extra text\n"
)


def see_useless_yes(text: str, missing: list) -> bool:
    """
    Check if text is useless for filling missing fields.

    Args:
        text: Input text to check
        missing: List of missing field names

    Returns:
        True if text is useless (contains no relevant info)
        False if text is useful (contains at least one relevant field)
    """
    # Empty text or nothing missing = useless
    if not text or not missing:
        return True

    client, model = get_model()

    messages = [
        {
            "role": "system",
            "content": SEE_USELESS_SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"Missing fields:\n{missing}"
        },
        {
            "role": "user",
            "content": text
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )

    output = response.choices[0].message.content.strip().upper()
    
    # DEBUG: Print what LLM returned
    print(f"[see_useless] Input: '{text[:50]}...' | LLM Output: '{output}' | Missing count: {len(missing)}")

    # YES → useless → True
    # NO  → useful  → False
    return output == "YES"
