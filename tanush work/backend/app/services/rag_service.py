import httpx
from app.services.mongodb_service import get_db
from app.config import OLLAMA_BASE_URL

DEFAULT_OLLAMA_URL = "http://localhost:11434"
# Use the concrete embedding model tag you have pulled locally
# e.g. `ollama pull nomic-embed-text:v1.5`
EMBEDDING_MODEL = "nomic-embed-text:v1.5"


async def create_embedding(text: str):
    """Create embedding using Ollama API"""
    base_url = OLLAMA_BASE_URL or DEFAULT_OLLAMA_URL
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/api/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": text
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
    except Exception as e:
        # Fallback: return empty embedding if Ollama fails
        # In production, you might want to handle this differently
        print(f"Warning: Embedding creation failed: {e}")
        return []



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
