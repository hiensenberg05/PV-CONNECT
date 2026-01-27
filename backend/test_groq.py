import asyncio
from app.config import settings
from app.services.llm_service import llm_service

async def test_groq():
    print("Testing Groq Generation...")
    
    if not settings.GROQ_API_KEY:
        print("SKIP: GROQ_API_KEY not set in settings")
        return

    try:
        response = await llm_service.generate_text("Say 'Hello Groq!'")
        print(f"Response: {response}")
        
        # Test JSON
        print("\nTesting JSON mode...")
        schema = {"type": "object", "properties": {"greeting": {"type": "string"}}}
        json_response = await llm_service.generate_text(
            "Return a JSON greeting", 
            response_schema=schema
        )
        print(f"JSON Response: {json_response}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
