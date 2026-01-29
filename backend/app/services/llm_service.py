import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # 🔴 THIS LINE IS IMPORTANT

_client = None
DEFAULT_MODEL = "llama-3.1-8b-instant"

def get_model(model: str | None = None):
    global _client

    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    return _client, model if model else DEFAULT_MODEL
