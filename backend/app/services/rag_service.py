import google.generativeai as genai
from app.services.mongodb_service import get_db


async def create_embedding(text: str):
    """Create embedding using Gemini API"""
    result = genai.embed_content(model="models/text-embedding-004", content=text)
    return result["embedding"]



async def find_similar_cases(query_text: str, limit: int = 10):
    db = get_db()
    query_embedding = await create_embedding(query_text)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": limit,
            }
        },
        {"$project": {"case_id": 1, "text": 1, "metadata": 1, "score": {"$meta": "vectorSearchScore"}}},
    ]
    return list(db.vectors.aggregate(pipeline))
