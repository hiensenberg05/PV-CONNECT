# Services module

from .ollama_service import (
    get_model,
    detect_language,
    extract_adverse_event,
    detect_user_type_from_message,
    triage_case,
    generate_followup,
)
from .mongodb_service import (
    get_db,
    get_drug_profile,
    upsert_case,
    get_case_by_id,
    find_user,
    save_message,
)
from .cloudinary_service import upload_bytes
from .rag_service import find_similar_cases

__all__ = [
    # Ollama services
    "get_model",
    "detect_language",
    "extract_adverse_event",
    "detect_user_type_from_message",
    "triage_case",
    "generate_followup",
    # MongoDB services
    "get_db",
    "get_drug_profile",
    "upsert_case",
    "get_case_by_id",
    "find_user",
    "save_message",
    # Cloudinary services
    "upload_bytes",
    # RAG services
    "find_similar_cases",
]


