# backend/app/services/see_useless.py
"""
Service to check if text input is useful for filling missing fields.
Uses LLM to make the determination.
"""

from app.services.llm_service import get_model


SEE_USELESS_SYSTEM_PROMPT = (
    "You are a Pharmacovigilance Information Validator.\n\n"
    "Your task: Determine if user input contains ANY useful medical/clinical information OR relevant conversational context.\n"
    "The user may speak in English, Hindi, or Hinglish.\n\n"
    
    "CRITICAL BIAS: **Always bias towards NO (USEFUL).**\n"
    "If the user is frustrated, referencing a previous message, or providing feedback, mark it as USEFUL (NO).\n"
    "We only want to block meaningless noise like single emojis or one-word greetings that are clearly just pleasantries.\n\n"
    
    "USEFUL INPUT (output NO):\n"
    "- Any medical info: 'Bhawasir', 'Dard', 'Tablet', '25 years', 'Male'\n"
    "- References to context: 'I just told you', 'Upar dekho', 'Already sent'\n"
    "- Frustration/Feedback: 'Why keep asking?', 'You are stupid', 'Talk to human'\n"
    "- Clarifications: 'What do you mean?', 'Kaunsa?'\n"
    "- Confirmation: 'Haan', 'Yes', 'Correct', 'Theek hai' (Contextually useful)\n"
    "- Negation: 'Nahi', 'No', 'Kuch nahi' (Contextually useful)\n\n"
    
    "USELESS INPUT (output YES):\n"
    "- Pure pleasantries alone: 'Hello', 'Hi', 'Gm', 'Good morning'\n"
    "- Random Emojis alone: '👍', '😊'\n"
    "- Gibberish: 'asdf', '...' \n\n"
    
    "DECISION RULES:\n"
    "1. Does it contain medical info? → NO\n"
    "2. Is the user angry, confused, or referring to past context? → NO\n"
    "3. Is it a direct answer (Yes/No)? → NO\n"
    "4. Is it JUST a greeting/emoji? → YES\n"
    "5. **DEFAULT: When uncertain, output NO**\n\n"
    
    "OUTPUT FORMAT:\n"
    "- Output ONLY: YES or NO\n"
    "- YES = useless (block it)\n"
    "- NO = useful (pass to agent)\n"
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
