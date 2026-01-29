# backend/app/workflows/router.py
"""
Router for determining user type (patient/doctor).
Uses exact string extraction - pinpoint matching.
"""

from typing import Optional, Tuple


# Exact keywords for matching (lowercase)
PATIENT_KEYWORDS = ["patient", "mareez", "bimar", "मरीज", "पेशेंट", "1"]
DOCTOR_KEYWORDS = ["doctor", "dr", "physician", "डॉक्टर", "चिकित्सक", "2"]


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
        "🏥 *Welcome to PV-CONNECT!*\n\n"
        "I'm here to help you report medicine side effects.\n\n"
        "Kya aap *Patient* hain ya *Doctor*?\n\n"
        "👤 Reply *1* or *Patient*\n"
        "👨‍⚕️ Reply *2* or *Doctor*"
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
