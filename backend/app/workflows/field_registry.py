from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FieldMeta:
    """
    Metadata definition for a single PvPI field.
    This file contains NO logic — only static truth.
    """

    field_name: str
    section: int  # PvPI section number (1–7)
    required: bool

    # Questions
    question_en: str
    question_hi: Optional[str] = None

    # Input handling
    field_type: str = "text"  
    options: Optional[List[str]] = None

    # Extraction & dependencies
    extractable_from_ocr: bool = False
    depends_on: Optional[str] = None
    depends_on_value: Optional[str] = None

    # Advanced behavior
    repeatable: bool = False
    prefill_from: Optional[str] = None


# ------------------------------------------------------------------
# PvPI FIELD REGISTRY (ORDER MATTERS)
# ------------------------------------------------------------------

FIELD_REGISTRY: Dict[str, FieldMeta] = {

    # -------------------------
    # SECTION 1 — PATIENT DETAILS
    # -------------------------

    "patient_initials": FieldMeta(
        field_name="patient_initials",
        section=1,
        required=True,
        question_en="What are the patient's initials?",
        question_hi="मरीज के नाम के शुरुआती अक्षर क्या हैं?"
    ),

    "patient_age": FieldMeta(
        field_name="patient_age",
        section=1,
        required=True,
        question_en="What is the patient's age?",
        question_hi="मरीज की उम्र क्या है?"
    ),

    "patient_gender": FieldMeta(
        field_name="patient_gender",
        section=1,
        required=True,
        field_type="select",
        options=["Male", "Female", "Other"],
        question_en="What is the patient's gender?",
        question_hi="मरीज का लिंग क्या है?"
    ),

    # -------------------------
    # SECTION 2 — HEALTH INFORMATION
    # -------------------------

    "reason_for_medicine": FieldMeta(
        field_name="reason_for_medicine",
        section=2,
        required=True,
        question_en="Why was the medicine taken?",
        question_hi="दवा क्यों ली गई थी?",
        extractable_from_ocr=True
    ),

    "who_advised_medicine": FieldMeta(
        field_name="who_advised_medicine",
        section=2,
        required=False,
        question_en="Who advised the medicine?",
        question_hi="दवा किसने सलाह दी थी?"
    ),

    # -------------------------
    # SECTION 3 — REPORTER DETAILS
    # -------------------------

    "reporter_name": FieldMeta(
        field_name="reporter_name",
        section=3,
        required=True,
        question_en="What is your name?",
        question_hi="आपका नाम क्या है?"
    ),

    "reporter_phone": FieldMeta(
        field_name="reporter_phone",
        section=3,
        required=True,
        question_en="What is your phone number?",
        question_hi="आपका फोन नंबर क्या है?",
        prefill_from="phone_number"
    ),

    # -------------------------
    # SECTION 4 — MEDICINE DETAILS (REPEATABLE)
    # -------------------------

    "medicine_name": FieldMeta(
        field_name="medicine_name",
        section=4,
        required=True,
        repeatable=True,
        extractable_from_ocr=True,
        question_en="What is the name of the medicine?",
        question_hi="दवा का नाम क्या है?"
    ),

    "medicine_dosage": FieldMeta(
        field_name="medicine_dosage",
        section=4,
        required=False,
        repeatable=True,
        extractable_from_ocr=True,
        question_en="What was the dosage of the medicine?",
        question_hi="दवा की खुराक क्या थी?"
    ),

    # -------------------------
    # SECTION 5 — SIDE EFFECT DETAILS
    # -------------------------

    "side_effect_description": FieldMeta(
        field_name="side_effect_description",
        section=5,
        required=True,
        question_en="Please describe the side effect experienced.",
        question_hi="कृपया अनुभव किए गए दुष्प्रभाव का वर्णन करें।"
    ),

    "hospitalized": FieldMeta(
        field_name="hospitalized",
        section=5,
        required=False,
        field_type="select",
        options=["Yes", "No"],
        question_en="Did the patient require hospitalization?",
        question_hi="क्या मरीज को अस्पताल में भर्ती करना पड़ा?"
    ),

    # -------------------------
    # SECTION 6 — SEVERITY
    # -------------------------

    "severity": FieldMeta(
        field_name="severity",
        section=6,
        required=True,
        field_type="multiselect",
        options=["Mild", "Moderate", "Severe", "Life-threatening"],
        question_en="How severe was the reaction?",
        question_hi="प्रतिक्रिया कितनी गंभीर थी?"
    ),

    # -------------------------
    # SECTION 7 — FINAL DESCRIPTION
    # -------------------------

    "management_action": FieldMeta(
        field_name="management_action",
        section=7,
        required=False,
        question_en="What action was taken to manage the reaction?",
        question_hi="प्रतिक्रिया को संभालने के लिए क्या किया गया?"
    ),
}
