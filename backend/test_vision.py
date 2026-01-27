import asyncio
from app.config import settings
from app.services.llm_service import llm_service
import base64

async def test_vision():
    print("Testing Gemini Vision...")
    
    if not settings.GEMINI_API_KEY:
        print("SKIP: GEMINI_API_KEY not set")
        return

    # Create a small 1x1 white pixel image for testing
    # Base64 for 1x1 white pixel JPEG
    tiny_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(tiny_pixel)

    try:
        response = await llm_service.extract_from_image(
            image_data=image_bytes,
            prompt="What color is this image?",
            response_schema={"type": "object", "properties": {"color": {"type": "string"}}}
        )
        print(f"Vision Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_vision())
