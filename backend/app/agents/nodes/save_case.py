from datetime import datetime
from app.services.mongodb_service import get_db
from app.services.rag_service import create_embedding
from app.agents.state import CaseState


async def save_case_node(state: CaseState) -> CaseState:
    db = get_db()
    case_id = state.get("case_id") or f"CASE_{datetime.utcnow().isoformat()}"
    state["case_id"] = case_id

    db.cases.insert_one({"_id": case_id, **state})

    text = f"Drug: {state.get('extracted_data', {}).get('drug_name')}; Symptoms: {state.get('extracted_data', {}).get('symptoms', [])}"
    embedding = await create_embedding(text)
    db.vectors.insert_one(
        {
            "case_id": case_id,
            "text": text,
            "embedding": embedding,
            "metadata": {"country": state.get("country")},
            "created_at": datetime.utcnow(),
        }
    )
    return state
