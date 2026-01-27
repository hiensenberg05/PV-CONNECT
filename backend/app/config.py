"""
Configuration management for NOVA Pharmacovigilance Assistant
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Gemini AI Configuration (Legacy)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_TEXT_MODEL: str = "gemini-2.5-flash"
    GEMINI_VISION_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TEXT_MODEL: str = "llama3:latest"
    OLLAMA_VISION_MODEL: str = "llama3.2-vision:latest" 
    OLLAMA_TIMEOUT_TEXT: float = 300.0   # Increased to 5 minutes for slow CPUs
    OLLAMA_TIMEOUT_VISION: float = 300.0 # Increased to 5 minutes
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "pv_connect"
    
    # Cloudinary Configuration (for document storage)
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # WhatsApp Configuration (deferred for now)
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None
    
    # Application Configuration
    APP_NAME: str = "NOVA Pharmacovigilance Assistant"
    APP_VERSION: str = "1.1"
    DEBUG: bool = False
    
    # Workflow Configuration
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: list[str] = ["en", "hi", "fr", "es", "de"]
    
    # Pharmacovigilance Configuration
    REQUIRED_FIELDS: list[str] = [
        "patient_age",
        "patient_gender",
        "drug_name",
        "symptoms",
        "timeline"
    ]
    COMPLETENESS_THRESHOLD: float = 0.7
    CONFIDENCE_THRESHOLD: float = 0.6
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
