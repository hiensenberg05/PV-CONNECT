import os
from pathlib import Path
from dotenv import load_dotenv

# Get the backend directory (where this file is)
BACKEND_DIR = Path(__file__).parent.parent
# Go up one level to parent directory
PARENT_DIR = BACKEND_DIR.parent

# Try loading .env from parent directory first, then backend directory
load_dotenv(PARENT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env")  # Fallback to backend/.env if exists

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "pv_connect")

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
