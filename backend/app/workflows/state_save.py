# backend/app/workflows/state_save.py
"""
Save conversation state to MongoDB.
Converts conversation state to Case format for final storage.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from app.db.mongo_db import mongodb_service
from app.schemas.case import Case, CaseData, PatientDetails, MedicineDetail, ReactionDetails


def safe_int(value: Any) -> Optional[int]:
    """Safely convert value to int. Returns None if not possible."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # Try to extract digits
        try:
            return int(value)
        except ValueError:
            # Try extracting first number from string like "65 years" or "unknown"
            import re
            match = re.search(r'\d+', value)
            if match:
                return int(match.group())
            return None
    return None


def convert_state_to_case(state: Dict[str, Any]) -> Case:
    """
    Convert conversation state (extracted_data) to Case format.
    Maps flat extracted_data keys to nested Case structure.
    """
    extracted = state.get("extracted_data", {})

    # Build patient details
    patient_details = PatientDetails(
        name=extracted.get("patient_name"),
        gender=extracted.get("patient_gender"),
        age_value=safe_int(extracted.get("patient_age_value")),
        age_unit=extracted.get("patient_age_unit")
    )

    # Build medicine details (currently single medicine, but list for future)
    medicine = MedicineDetail(
        name=extracted.get("medicine_name"),
        quantity_taken=extracted.get("medicine_quantity_taken"),
        dosage_form=extracted.get("medicine_dosage_form"),
        expiry_date=extracted.get("medicine_expiry_date"),
        start_date=extracted.get("medicine_start_date"),
        stop_date=extracted.get("medicine_stop_date"),
        reason_for_medicine=extracted.get("reason_for_medicine"),
        advised_by=extracted.get("medicine_advised_by"),
        self_medicated=extracted.get("self_medicated")
    )
    medicine_details = [medicine] if medicine.name else []

    # Build reaction details
    reaction_details = ReactionDetails(
        start_date=extracted.get("side_effect_start_date"),
        continuing=extracted.get("side_effect_continuing"),
        stop_date=extracted.get("side_effect_stop_date")
    )

    # Build severity list
    severity = []
    if extracted.get("severity_no_daily_activity_effect"):
        severity.append("no_daily_activity_effect")
    if extracted.get("severity_affected_daily_activity"):
        severity.append("affected_daily_activity")
    if extracted.get("severity_hospitalized"):
        severity.append("hospitalized")
    if extracted.get("severity_death"):
        severity.append("death")
    if extracted.get("severity_other"):
        severity.append(f"other: {extracted.get('severity_other')}")

    # Build case data
    case_data = CaseData(
        patient_details=patient_details,
        medicine_details=medicine_details,
        reaction_details=reaction_details,
        severity=severity,
        description=extracted.get("side_effect_description", ""),
        management_action=extracted.get("management_action_taken"),
        past_disease_history=extracted.get("past_disease_history")
    )

    # Build final case
    case = Case(
        case_id=state.get("case_id", ""),
        patient_phone=state.get("phone_number", ""),
        reporter_type=state.get("user_type", "patient"),
        data=case_data,
        is_complete=state.get("case_complete", False),
        created_at=state.get("created_at", datetime.utcnow()),
        updated_at=datetime.utcnow()
    )

    return case


async def save_state(state: Dict[str, Any]) -> bool:
    """
    Save conversation state to MongoDB.
    Saves to two collections:
    1. conversation_states - full state for resuming
    2. cases - final case data in proper format (when complete)
    """
    phone_number = state.get("phone_number")
    if not phone_number:
        raise ValueError("state must have 'phone_number'")

    state["last_updated"] = datetime.utcnow()

    # Save full state to conversation_states
    await mongodb_service.db.conversation_states.update_one(
        {"phone_number": phone_number},
        {"$set": state},
        upsert=True
    )

    # If case is complete, also save to cases collection in proper format
    if state.get("case_complete") is True:
        case = convert_state_to_case(state)
        case_doc = case.to_mongo_doc()

        await mongodb_service.db.cases.update_one(
            {"case_id": case.case_id},
            {"$set": case_doc},
            upsert=True
        )

    return True


async def save_case_only(state: Dict[str, Any]) -> str:
    """
    Save only the Case (not full state).
    Used when case is complete and we want to save final data.
    Returns case_id.
    """
    case = convert_state_to_case(state)
    case_doc = case.to_mongo_doc()

    await mongodb_service.db.cases.update_one(
        {"case_id": case.case_id},
        {"$set": case_doc},
        upsert=True
    )

    return case.case_id
