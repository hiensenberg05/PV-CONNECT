# schemas/pvpi_form.py

class PatientDetails(BaseModel):
    initials: Optional[str] = None
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    age_value: Optional[int] = None
    age_unit: Optional[Literal["Year", "Month"]] = None

class HealthInformation(BaseModel):
    reason_for_medicine: Optional[str] = None
    medicine_advised_by: Optional[Literal["Doctor", "Pharmacist", "Friends / Relatives", "Self"]] = None
    past_disease_history: Optional[bool] = None

class ReporterDetails(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class MedicineDetails(BaseModel):
    medicine_name: Optional[str] = None
    quantity_taken: Optional[str] = None
    dosage_form: Optional[Literal["Tablet", "Capsule", "Injection", "Oral liquid", "Other"]] = None
    expiry_date: Optional[str] = None  # DD/MM/YYYY
    start_date: Optional[str] = None
    stop_date: Optional[str] = None

class SideEffectDetails(BaseModel):
    side_effect_start_date: Optional[str] = None
    is_continuing: Optional[bool] = None
    stop_date: Optional[str] = None

class SeverityDetails(BaseModel):
    did_not_affect_daily_activities: bool = False
    affected_daily_activities: bool = False
    admitted_to_hospital: bool = False
    death: bool = False
    others: Optional[str] = None

class DescriptionDetails(BaseModel):
    side_effect_description: Optional[str] = None  # or general health concern
    management_action: Optional[str] = None

class PvPIForm(BaseModel):
    section_1_patient: PatientDetails
    section_2_health: HealthInformation
    section_3_reporter: ReporterDetails
    section_4_medicines: List[MedicineDetails] = []
    section_5_side_effect: SideEffectDetails
    section_6_severity: SeverityDetails
    section_7_description: DescriptionDetails

class ConversationState(BaseModel):
    session_id: UUID
    user_role: Literal["PATIENT", "DOCTOR"]
    language: str
    workflow_stage: str  # PVPI_SECTION_1, PVPI_SECTION_2, etc.
    pvpi_form: PvPIForm
    case_id: Optional[UUID] = None
    pending_fields: List[str] = []
    documents: List[str] = []
    metadata: dict = {}