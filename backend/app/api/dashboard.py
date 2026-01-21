from fastapi import APIRouter
from app.services.mongodb_service import get_db

router = APIRouter()


@router.get("/cases")
async def list_cases():
    db = get_db()
    cases = list(db.cases.find().sort("created_at", -1).limit(50))
    for c in cases:
        c["_id"] = str(c["_id"])
    return cases
