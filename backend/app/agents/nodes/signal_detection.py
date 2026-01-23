from datetime import datetime, timedelta
import json

from app.services.mongodb_service import get_db
from app.services.rag_service import find_similar_cases
from app.services.gemini_service import get_model


async def detect_signals():
    """
    Periodic background job: aggregate last 7 days, detect spikes, analyze with Gemini.
    """
    db = get_db()
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)},
            }
        },
        {"$unwind": "$adverse_event.symptoms"},
        {
            "$group": {
                "_id": {
                    "drug": "$adverse_event.drug_name",
                    "symptom": "$adverse_event.symptoms",
                    "country": "$country",
                },
                "count": {"$sum": 1},
            }
        },
        {"$match": {"count": {"$gte": 5}}},
        {"$sort": {"count": -1}},
    ]

    signals = list(db.cases.aggregate(pipeline))
    model = get_model("gemini-2.5-flash")

    for signal in signals:
        query = f"Drug: {signal['_id']['drug']}, Symptom: {signal['_id']['symptom']}"
        similar_cases = await find_similar_cases(query, limit=20)
        prompt = f"""
        Assess safety signal.
        Current: {signal['count']} reports of {signal['_id']['symptom']} for {signal['_id']['drug']} in {signal['_id']['country']} (7d)
        Historical matches: {len(similar_cases)}
        Return JSON: {{"is_significant": true/false, "risk_level": "low|medium|high", "reasoning": "", "recommended_action": ""}}
        """
        response = model.generate_content(prompt)
        try:
            analysis = json.loads(response.text)
        except Exception:
            analysis = {"is_significant": False}

        db.signals.insert_one(
            {
                "drug": signal["_id"]["drug"],
                "symptom": signal["_id"]["symptom"],
                "country": signal["_id"]["country"],
                "count": signal["count"],
                "analysis": analysis,
                "detected_at": datetime.utcnow(),
                "status": "pending_review",
            }
        )

        # Import manager here to avoid circular import
        from app.api.websockets import manager
        await manager.broadcast({"type": "new_signal", "data": analysis})
