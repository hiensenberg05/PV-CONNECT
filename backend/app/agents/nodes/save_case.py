# from datetime import datetime
# from app.services.mongodb_service import get_db
# from app.services.rag_service import create_embedding
# from app.agents.state import CaseState


# async def save_case_node(state: CaseState) -> CaseState:
#     db = get_db()
#     case_id = state.get("case_id") or f"CASE_{datetime.utcnow().isoformat()}"
#     state["case_id"] = case_id

#     db.cases.insert_one({"_id": case_id, **state})

#     text = f"Drug: {state.get('extracted_data', {}).get('drug_name')}; Symptoms: {state.get('extracted_data', {}).get('symptoms', [])}"
#     embedding = await create_embedding(text)
#     db.vectors.insert_one(
#         {
#             "case_id": case_id,
#             "text": text,
#             "embedding": embedding,
#             "metadata": {"country": state.get("country")},
#             "created_at": datetime.utcnow(),
#         }
#     )
#     return state

from datetime import datetime
from app.services.mongodb_service import get_db
from app.services.rag_service import create_embedding
from app.agents.state import CaseState


async def save_case_node(state: CaseState) -> CaseState:
    db = get_db()

    # ✅ generate case_id only if missing
    case_id = state.get("case_id")
    if not case_id:
        case_id = f"CASE_{datetime.utcnow().isoformat()}"
        state["case_id"] = case_id

    # ✅ UPSERT instead of insert (LOGIC FIX)
    db.cases.update_one(
        {"_id": case_id},
        {
            "$set": state,
            "$setOnInsert": {"created_at": datetime.utcnow()},
        },
        upsert=True,
    )

    # ---- vector logic UNCHANGED ----
    text = (
        f"Drug: {state.get('extracted_data', {}).get('drug_name')}; "
        f"Symptoms: {state.get('extracted_data', {}).get('symptoms', [])}"
    )

    embedding = await create_embedding(text)

    # ✅ make vector write idempotent (LOGIC FIX)
    db.vectors.update_one(
        {"case_id": case_id},
        {
            "$set": {
                "case_id": case_id,
                "text": text,
                "embedding": embedding,
                "metadata": {"country": state.get("country")},
            },
            "$setOnInsert": {"created_at": datetime.utcnow()},
        },
        upsert=True,
    )

    return state

