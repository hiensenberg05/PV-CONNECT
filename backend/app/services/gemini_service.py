import google.generativeai as genai
from functools import lru_cache
from app.config import GEMINI_API_KEY


@lru_cache(maxsize=1)
def get_client():
    genai.configure(api_key=GEMINI_API_KEY)
    return genai


def get_model(name: str = "gemini-2.0-flash-exp"):
    client = get_client()
    return client.GenerativeModel(name)
