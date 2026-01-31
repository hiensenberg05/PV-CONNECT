# backend/app/services/see_useless.py
"""
Service to check if text input is useful for filling missing fields.
Uses LLM to make the determination.

FIXED VERSION:
- More permissive (bias towards accepting input)
- Better handling of short inputs
- Context-aware validation
"""

from app.services.llm_service import get_model


SEE_USELESS_SYSTEM_PROMPT = (
    "You are a Pharmacovigilance Input Validator.\n\n"
    "Task: Determine if user input contains ANY useful information for medical data collection.\n"
    "User may speak English, Hindi, or Hinglish.\n\n"
    
    "**CRITICAL RULE: BIAS TOWARDS ACCEPTING INPUT (output NO)**\n"
    "When in doubt, output NO (useful). We prefer false positives over false negatives.\n\n"
    
    "USEFUL INPUT (output NO):\n"
    "- Any medical/health info: 'fever', 'dard', 'bukhar', 'tablet', 'pain'\n"
    "- Names: 'Rahul', 'Priya', 'Amit', 'Harsh' (even single names)\n"
    "- Numbers: '25', '500mg', '2 tablets'\n"
    "- Gender: 'male', 'female', 'ladka', 'ladki', 'aadmi'\n"
    "- Dates: '12/26', 'yesterday', 'last week'\n"
    "- Medicine names: 'pudanahara', 'paracetamol', 'dolo'\n"
    "- Yes/No answers: 'yes', 'no', 'haan', 'nahi'\n"
    "- Denials: 'I don't have', 'nahi hai', 'nothing'\n"
    "- References: 'I told you', 'already sent', 'upar dekho'\n"
    "- Frustration: 'Why again?', 'not working', 'stupid bot'\n\n"
    
    "USELESS INPUT (output YES) - ONLY THESE:\n"
    "- Pure greetings ALONE: 'hi', 'hello', 'hey', 'namaste'\n"
    "- Just emojis: '👍', '😊'\n"
    "- Gibberish: 'asdf', 'xyz', '...'\n"
    "- Random text with no context\n\n"
    
    "DECISION TREE:\n"
    "1. Contains ANY number/name/date? → NO (useful)\n"
    "2. Contains ANY medical term? → NO (useful)\n"
    "3. Is it yes/no/confirmation? → NO (useful)\n"
    "4. User seems confused/frustrated? → NO (useful - we need to handle it)\n"
    "5. ONLY greeting/emoji with nothing else? → YES (useless)\n"
    "6. **DEFAULT: Output NO**\n\n"
    
    "OUTPUT FORMAT:\n"
    "Output ONLY one word: YES or NO\n"
    "- YES = completely useless (pure greeting/emoji)\n"
    "- NO = contains useful info (accept it)\n"
)


def see_useless_yes(text: str, missing: list) -> bool:
    """
    Check if text is useless for filling missing fields.
    
    FIXED LOGIC:
    - More permissive (bias towards accepting)
    - Better short input handling
    - Context awareness
    
    Args:
        text: Input text to check
        missing: List of missing field names

    Returns:
        True if text is COMPLETELY useless (pure greeting/emoji)
        False if text contains ANY potentially useful info
    """
    # Empty text = useless
    if not text or not text.strip():
        return True
    
    # NEW: If missing list is empty, still validate input
    # (User might be providing additional context)
    
    text = text.strip()
    
    # NEW: Quick validation for obvious useful inputs (skip LLM call)
    # If input contains digits, likely useful
    if any(c.isdigit() for c in text):
        print(f"[see_useless] '{text[:50]}' → Contains digits → USEFUL (skipped LLM)")
        return False
    
    # If input is longer than 3 words, likely useful
    word_count = len(text.split())
    if word_count > 3:
        print(f"[see_useless] '{text[:50]}' → {word_count} words → USEFUL (skipped LLM)")
        return False
    
    # NEW: Common useful single-word answers (skip LLM)
    useful_single_words = {
        'yes', 'no', 'haan', 'nahi', 'male', 'female', 'ladka', 'ladki',
        'tablet', 'capsule', 'syrup', 'injection', 'goli', 'dawai',
        'aadmi', 'aurat', 'purush', 'mahila', 'boy', 'girl', 'man', 'woman'
    }
    if text.lower() in useful_single_words:
        print(f"[see_useless] '{text}' → Known useful word → USEFUL (skipped LLM)")
        return False
    
    # Use LLM for ambiguous cases
    client, model = get_model()

    messages = [
        {
            "role": "system",
            "content": SEE_USELESS_SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"Current missing fields (for context): {', '.join(missing[:10])}"
        },
        {
            "role": "user",
            "content": text
        }
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=5
        )

        output = response.choices[0].message.content.strip().upper()
        
        # Parse output
        is_useless = output == "YES"
        
        # DEBUG: Print decision
        status = "USELESS ❌" if is_useless else "USEFUL ✓"
        print(f"[see_useless] '{text[:50]}' → {output} → {status}")
        
        return is_useless
        
    except Exception as e:
        # On error, assume useful (fail-open)
        print(f"[see_useless] ERROR: {e} → Defaulting to USEFUL")
        return False