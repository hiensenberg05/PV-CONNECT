# backend/app/services/convert_lang_msg.py
"""
Language conversion service using LLM.
Converts text to the specified language.
"""

from app.services.llm_service import get_model


def convert_to_language(text: str, language: str) -> str:
    """
    Convert text to the specified language using LLM.
    
    Args:
        text: The text to convert
        language: Target language code (e.g., 'hi', 'en', 'hi_en', 'ta', 'te')
    
    Returns:
        Converted text in the target language, or original if no language specified
    """
    # If no text, return as-is
    if not text or not text.strip():
        return text
    
    # If no language specified or English, return original text (no conversion)
    if not language or language == "en":
        return text
    
    # Language mapping
    lang_names = {
        "hi": "Hindi (Devanagari script)",
        "hi_en": "Hinglish (Hindi in Roman/English letters)",
        "ta": "Tamil",
        "te": "Telugu",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "ur": "Urdu",
        "pa": "Punjabi"
    }
    
    target_lang = lang_names.get(language)
    
    # If unknown language code, return original
    if not target_lang:
        return text
    
    client, model = get_model()
    
    system_prompt = (
        f"You are a translator. Convert the following text to {target_lang}.\n\n"
        "Rules:\n"
        "- Output ONLY the translated text\n"
        "- No explanations\n"
        "- Keep the meaning and tone\n"
        "- If already in target language, return as-is"
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception:
        return text  # Return original if translation fails
