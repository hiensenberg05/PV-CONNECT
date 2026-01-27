# from app.services.mongodb_service import get_db
# from app.agents.state import CaseState


# async def check_compliance_node(state: CaseState) -> CaseState:
#     db = get_db()
#     template = db.compliance_templates.find_one({"country": state.get("country", "IN")})
#     mandatory = template["mandatory_fields"] if template else []
#     extracted = state.get("extracted_data", {})
#     missing = [f for f in mandatory if not extracted.get(f)]
#     completeness = (len(mandatory) - len(missing)) / len(mandatory) if mandatory else 0

#     state["missing_fields"] = missing
#     state["completeness_score"] = completeness
#     state["requires_followup"] = completeness < 0.7 if mandatory else True
#     return state

# from app.agents.state import CaseState

# # Global mandatory schema (country-agnostic)
# MANDATORY_FIELDS = [
#     "drug_name",
#     "symptoms",
#     "severity",
#     "start_date",
#     "dosage",
# ]

# async def check_compliance_node(state: CaseState) -> CaseState:
#     extracted = state.get("extracted_data", {})
#     documents = state.get("documents", [])

#     missing = []

#     # 1️⃣ Check mandatory structured fields
#     for field in MANDATORY_FIELDS:
#         if not extracted.get(field):
#             missing.append(field)

#     # 2️⃣ Check for bill / prescription image
#     if not documents:
#         missing.append("bill_or_prescription")

#     # 3️⃣ Compute completeness (0–100)
#     total_required = len(MANDATORY_FIELDS) + 1  # +1 for document
#     completeness = int(
#         100 * (total_required - len(missing)) / total_required
#     )

#     state["missing_fields"] = missing
#     state["completeness_score"] = completeness
#     state["requires_followup"] = len(missing) > 0

#     return state



from app.agents.state import CaseState
from app.agents.nodes.ocr_processing import process_image_node
from app.agents.nodes.voice_processing import process_voice_node

# Global mandatory schema (country-agnostic)
MANDATORY_FIELDS = [
    "drug_name",
    "symptoms",
    "severity",
    "start_date",
    "dosage",
]


async def check_compliance_node(state: CaseState) -> CaseState:
    # ===============================
    # 🔹 STEP 0: RUN IMAGE + VOICE NODES
    # ===============================

    # Run OCR if document exists
    if state.get("documents_id"):
        state = await process_image_node(state)

    # Run voice processing if voice note exists
    if state.get("voice_notes_id"):
        state = await process_voice_node(state)

    # ===============================
    # 🔹 STEP 1: COLLECT EXTRACTED DATA
    # ===============================

    extracted = state.get("extracted_data", {})

    # Latest OCR extracted data
    doc_extracted = {}
    documents = state.get("documents", [])
    if documents:
        doc_extracted = documents[-1].get("ocr_data", {})

    # Voice-extracted data (already NLP-processed)
    voice_extracted = state.get("voice_extracted_data", {})

    # ===============================
    # 🔹 STEP 2: MERGE (text < OCR < voice)
    # ===============================

    for source in [doc_extracted, voice_extracted]:
        for key, value in source.items():
            if value not in (None, "", [], {}):
                extracted[key] = value

    state["extracted_data"] = extracted

    # ===============================
    # 🔹 STEP 3: ORIGINAL COMPLIANCE LOGIC
    # ===============================

    missing = []

    # 1️⃣ Check mandatory structured fields
    for field in MANDATORY_FIELDS:
        if not extracted.get(field):
            missing.append(field)

    # 2️⃣ Check for bill / prescription image
    # if not documents:
    #     missing.append("bill_or_prescription")

    # 3️⃣ Compute completeness (0–100)
    total_required = len(MANDATORY_FIELDS) + 1
    completeness = int(
        100 * (total_required - len(missing)) / total_required
    )

    state["missing_fields"] = missing
    state["completeness_score"] = completeness
    state["requires_followup"] = len(missing) > 0

    return state
