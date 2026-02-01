import os
from dotenv import load_dotenv
from groq import Groq

# Import centralized settings (handles .env loading)
from app.config import settings

_client = None
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_model(model: str | None = None):
    global _client

    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)

    return _client, model if model else DEFAULT_MODEL
