"""
LLM Service using Ollama
Replaces Gemini with local llama3 and llama3.2-vision models
"""

import json
import logging
from typing import Optional, Dict, Any, List
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

# =========================================================
# Custom Exceptions
# =========================================================

class RateLimitError(Exception):
    """Raised when API rate limit is hit (kept for compatibility)"""
    pass

class LLMError(Exception):
    """General LLM error"""
    pass

# =========================================================
# Ollama Service
# =========================================================

class OllamaService:
    """Service wrapper for Ollama models"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.text_model = settings.OLLAMA_TEXT_MODEL
        self.vision_model = settings.OLLAMA_VISION_MODEL
        
        logger.info(
            f"OllamaService initialized | "
            f"base_url={self.base_url} | "
            f"text_model={self.text_model} | "
            f"vision_model={self.vision_model}"
        )

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------
    def _clean_json_text(self, text: str) -> str:
        """Clean JSON text by removing markdown formatting"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _extract_first_json_object(self, text: str) -> str:
        """Best-effort extraction of JSON object/array from response."""
        text = self._clean_json_text(text)
        
        # Fast path
        if (text.startswith("{") and text.endswith("}")) or \
           (text.startswith("[") and text.endswith("]")):
            return text

        # Find first JSON object
        start_obj = text.find("{")
        end_obj = text.rfind("}")
        if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
            return text[start_obj : end_obj + 1].strip()

        # Find first JSON array
        start_arr = text.find("[")
        end_arr = text.rfind("]")
        if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
            return text[start_arr : end_arr + 1].strip()

        return text


    # -----------------------------------------------------
    # Core Text Generation
    # -----------------------------------------------------
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[dict] = None
    ) -> str:
        """
        Generate text from Ollama.
        Matches GeminiService signature for compatibility.
        """
        try:
            # Construct payload
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.text_model,
                "prompt": prompt, 
                "system": system_instruction if system_instruction else "",
                "stream": False,
                "options": {
                    "temperature": settings.GEMINI_TEMPERATURE, 
                    "num_predict": settings.GEMINI_MAX_TOKENS,
                }
            }

            # Handle Schema / JSON Mode
            if response_schema:
                payload["format"] = "json"
                # Append schema instruction to prompt to ensure adherence
                schema_str = json.dumps(response_schema, indent=2)
                payload["prompt"] = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON matching this schema:\n{schema_str}"

            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_TEXT) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                response_text = result.get("response", "")

                if response_schema:
                    return self._extract_first_json_object(response_text)
                return response_text

        except httpx.TimeoutException:
            logger.error(f"Ollama request timeout for model {self.text_model}")
            raise RateLimitError("Ollama timeout") 
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    # -----------------------------------------------------
    # Vision / OCR Extraction
    # -----------------------------------------------------
    async def extract_from_image(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: str = "image/jpeg", 
        response_schema: Optional[dict] = None
    ) -> str:
        """
        Extract structured information from image using Ollama Vision.
        """
        try:
            import base64
            # Convert bytes to base64 string
            if isinstance(image_data, bytes):
                b64_image = base64.b64encode(image_data).decode('utf-8')
            else:
                b64_image = image_data 

            payload = {
                "model": self.vision_model,
                "prompt": prompt,
                "images": [b64_image],
                "stream": False,
                "options": {
                    "temperature": settings.GEMINI_TEMPERATURE,
                }
            }

            if response_schema:
                payload["format"] = "json"
                schema_str = json.dumps(response_schema, indent=2)
                payload["prompt"] = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON matching this schema:\n{schema_str}"

            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_VISION) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                response_text = result.get("response", "")

                if response_schema:
                    return self._extract_first_json_object(response_text)
                return response_text

        except Exception as e:
            logger.error(f"Ollama vision error: {e}")
            raise

    # -----------------------------------------------------
    # Compatibility Methods
    # -----------------------------------------------------
    async def classify_initial_message(self, text: str) -> Dict[str, str]:
        """
        Specific workflow method - implemented using Ollama
        """
        from pathlib import Path
        try:
            # We need to manually load the prompt here since we are inside the class
            # This logic mimics the original class
            prompt_path = (
                Path(__file__).parent.parent
                / "shared_prompts"
                / "initial_classification.txt"
            )
            
            if prompt_path.exists():
                system_prompt = prompt_path.read_text(encoding="utf-8")
            else:
                # Fallback if file not found
                system_prompt = "Detect language and user type. Return JSON: {\"language\": \"en\", \"user_type\": \"patient\"}"

            full_prompt = f"User message:\n{text}"
            
            # Use generate_text
            response_json = await self.generate_text(
                prompt=full_prompt,
                system_instruction=system_prompt,
                response_schema={"type": "object"} # Just trigger JSON mode
            )

            data = json.loads(response_json)
            
            return {
                "language": data.get("language", "en"),
                "user_type": data.get("user_type", "patient")
            }

        except Exception as e:
            logger.error(f"Initial classification failed: {e}")
            return {
                "language": "en",
                "user_type": "patient"
            }

# =========================================================
# Singleton Instance
# =========================================================

# Expose as 'gemini_service' for backward compatibility with graph.py
gemini_service = OllamaService()
# Also expose as generic name
llm_service = gemini_service
