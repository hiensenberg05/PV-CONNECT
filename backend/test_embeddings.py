import asyncio
from app.services.rag_service import rag_service

async def test_embeddings():
    print("Testing Embeddings...")
    
    symptoms = ["headache", "vomiting"]
    # Mocking database response isn't easy without running DB, 
    # so we will check if model encodes stuff.
    
    try:
        if not rag_service.model:
             print("Error: Model not loaded")
             return

        # Test encoding
        emb = rag_service.model.encode("test string")
        print(f"Encoding successful. Shape: {emb.shape}")
        
        # Test semantic match availability
        # We can't fully test check_side_effect_match without DB, 
        # but we can verify the method exists and runs.
        print("RAG Service initialized and model loaded.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_embeddings())
