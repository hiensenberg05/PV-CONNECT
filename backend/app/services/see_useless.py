# backend/app/services/see_useless.py
"""
Service to check if text input is useful for filling missing fields.
Uses LLM to make the determination.
"""

from app.services.llm_service import get_model


SEE_USELESS_SYSTEM_PROMPT = (
    "You are a Pharmacovigilance Information Checker.\n\n"
    "Your task is to decide whether the given text is USELESS for filling missing information.\n\n"
    "You will be provided with:\n"
    "- A text input\n"
    "- A list of missing field names\n\n"
    "Rules:\n"
    "1. Check whether the text clearly contains information for ANY of the missing fields.\n"
    "2. Do NOT guess or infer information.\n"
    "3. If the text contains information for AT LEAST ONE missing field, respond with exactly:\n"
    "NO\n"
    "4. If the text contains information for NONE of the missing fields, respond with exactly:\n"
    "YES\n\n"
    "Output rules:\n"
    "- Output ONLY YES or NO\n"
    "- YES means the text is useless\n"
    "- NO means the text is useful\n"
    "- No explanations\n"
    "- No JSON\n"
    "- No extra text\n"
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

    # YES → useless → True
    # NO  → useful  → False
    return output == "YES"
