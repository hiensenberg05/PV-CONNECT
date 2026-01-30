"""
Configuration Management for VigiGrade

This module provides centralized configuration for the VigiGrade system.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# Load .env from the root PV-CONNECT folder
root_dir = Path(__file__).resolve().parent.parent.parent.parent  # analytics/config.py -> PV-CONNECT
env_path = root_dir / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # MongoDB Configuration - use same as main app
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    database_name: str = os.getenv("MONGODB_DATABASE", "pv_connect")
    collection_name: str = "cases"
    
    # Worker Configuration
    batch_interval_minutes: int = 60
    enable_change_stream: bool = True
    max_retries: int = 3
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    
    # Scoring Configuration
    min_description_length: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Example .env file:
"""
# MongoDB
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=pharmacovigilance

# Worker
BATCH_INTERVAL_MINUTES=60
ENABLE_CHANGE_STREAM=true
MAX_RETRIES=3

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
"""
