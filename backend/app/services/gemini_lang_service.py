import google.generativeai as genai
from app.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

_model = genai.GenerativeModel(
    "models/gemini-pro-latest",
    generation_config={
        "temperature": 0,
        "max_output_tokens": 10,
    },
)

def detect_language(text: str) -> str:
    prompt = (
        "Detect the language of the text below.\n"
        "Reply ONLY with a 2-letter ISO 639-1 code.\n"
        "Examples: en, hi, fr, ta.\n\n"
        f"Text: {text}"
    )

    resp = _model.generate_content(prompt)
    return resp.text.strip().lower()
