# backend/app/workflows/router.py
"""
Router for determining user type (patient/doctor).
Uses exact string extraction - pinpoint matching.
"""

from typing import Optional, Tuple
from app.services.convert_lang_msg import convert_to_language



# Exact keywords for matching (lowercase)
PATIENT_KEYWORDS = ["patient", "mareez", "bimar", "मरीज", "पेशेंट", "1","१"]
DOCTOR_KEYWORDS = ["doctor", "dr", "physician", "डॉक्टर", "चिकित्सक", "2"]
NEW_CASE_KEYWORDS = ["new", "no", "nahi", "naya", "start", "fresh", "नया", "नहीं", "3"]
EXIT_KEYWORDS = ["exit", "quit", "bye", "stop", "end", "band", "बंद", "निकलना"]


def extract_user_type(message: str) -> Optional[str]:
    """
    Extract user type from message using exact string matching.
    This is for when bot asks "Are you Patient or Doctor?"
    
    Returns:
        'patient' | 'doctor' | None
    """
    if not message:
        return None
    
    # Clean and lowercase
    msg_clean = message.lower().strip()
    
    # Check for exact match first (single word reply)
    if msg_clean in PATIENT_KEYWORDS:
        return "patient"
    if msg_clean in DOCTOR_KEYWORDS:
        return "doctor"
    
    # Check if any keyword is present in the message
    for kw in DOCTOR_KEYWORDS:
        if kw in msg_clean:
            return "doctor"
    
    for kw in PATIENT_KEYWORDS:
        if kw in msg_clean:
            return "patient"
    
    return None


def get_user_type_question() -> str:
    """
    The hardcoded question to ask user type.
    """
    return (
        "🏥 *Welcome to PV-CONNECT*\n\n"
        "We are here to assist you in reporting Adverse Drug Reactions (ADRs) "
        "in a secure and confidential manner.\n\n"
        "*Please identify yourself:*\n\n"
        "👤 Reply *1* for *Patient*\n"
        "👨‍⚕️ Reply *2* for *Healthcare Professional*"
    )


def is_asking_user_type_stage(state: dict) -> bool:
    """
    Check if we are in the stage where we're waiting for user type.
    """
    return (
        state is None or
        state.get("user_type") is None or
        state.get("workflow_stage") == "ASK_USER_TYPE"
    )


def get_case_id_question() -> str:
    """
    Welcome message asking for Case ID first.
    """
    return (
        "🏥 *Welcome to PV-CONNECT*\n\n"
        "We assist you in reporting medicine-related adverse events safely and securely.\n\n"
        "*Do you have an existing Case ID?*\n\n"
        "📋 *Yes* — Please paste your Case ID\n"
        "🆕 *No* — Type *'new'* to begin a new report\n\n"
        "💡 _Tip: Type 'exit' at any time to save your progress and leave_"
    )


def is_new_case_request(message: str) -> bool:
    """
    Check if user wants to start a new case.
    """
    if not message:
        return False
    msg_clean = message.lower().strip()
    return msg_clean in NEW_CASE_KEYWORDS


def is_exit_request(message: str) -> bool:
    """
    Check if user wants to exit the chat.
    """
    if not message:
        return False
    msg_clean = message.lower().strip()
    return msg_clean in EXIT_KEYWORDS
