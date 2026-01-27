"""
LLM Service using Groq (Text) and Gemini (Vision)
Replaces local llama3 with Groq's llama-3.3 and Gemini 2.5 Flash
"""

import json
import logging
import base64
from typing import Optional, Dict, Any, List
# from groq import AsyncGroq # Assuming we still use Groq for text
import httpx
from groq import AsyncGroq
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

# =========================================================
# Custom Exceptions
# =========================================================

class RateLimitError(Exception):
    """Raised when API rate limit is hit"""
    pass

class LLMError(Exception):
    """General LLM error"""
    pass

# =========================================================
# Hybrid Service (Groq Text + Gemini Vision)
# =========================================================

class HybridLLMService:
    """Service wrapper for Groq (Text) and Gemini (Vision)"""

    def __init__(self):
        # Initialize Groq Client (Text)
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL
        self.groq_client = None
        
        if self.groq_api_key:
            self.groq_client = AsyncGroq(api_key=self.groq_api_key)
            logger.info(f"Groq Service initialized | text_model={self.groq_model}")
        else:
            logger.warning("GROQ_API_KEY not set! Text generation will fail.")

        # Initialize Gemini Client (Vision)
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_vision_model = settings.GEMINI_VISION_MODEL
        self.gemini_client = None

        if self.gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"Gemini Service initialized | vision_model={self.gemini_vision_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("GEMINI_API_KEY not set! Vision tasks will fail.")

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
    # Core Text Generation (Groq)
    # -----------------------------------------------------
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[dict] = None
    ) -> str:
        """
        Generate text using Groq.
        """
        if not self.groq_client:
             raise LLMError("Groq client not initialized. Check GROQ_API_KEY.")

        try:
            # Construct messages
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            # If schema is provided, append it to the prompt to force JSON
            final_prompt = prompt
            if response_schema:
                schema_str = json.dumps(response_schema, indent=2)
                final_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON matching this schema:\n{schema_str}"
                # Also ensure system prompt mentions JSON
                if system_instruction:
                     if "json" not in system_instruction.lower():
                         messages[0]["content"] += "\nReturn response in JSON format."
                else:
                     messages.insert(0, {"role": "system", "content": "You are a helpful assistant. Return response in JSON format."})

            messages.append({"role": "user", "content": final_prompt})
            
            # Call Groq API
            chat_completion = await self.groq_client.chat.completions.create(
                messages=messages,
                model=self.groq_model,
                temperature=settings.GEMINI_TEMPERATURE,
                max_tokens=settings.GEMINI_MAX_TOKENS,
                top_p=1,
                stop=None,
                stream=False,
                response_format={"type": "json_object"} if response_schema else None
            )

            response_text = chat_completion.choices[0].message.content

            if response_schema:
                return self._extract_first_json_object(response_text)
            return response_text

        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            if "rate limit" in str(e).lower() or "429" in str(e):
                raise RateLimitError("Groq Rate Limit Exceeded")
            raise LLMError(f"Groq error: {e}")

    # -----------------------------------------------------
    # Vision / OCR Extraction (Gemini 2.5 Flash)
    # -----------------------------------------------------
    async def extract_from_image(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: str = "image/jpeg", 
        response_schema: Optional[dict] = None
    ) -> str:
        """
        Extract structured information from image using Gemini 2.5 Flash.
        """
        if not self.gemini_client:
             raise LLMError("Gemini client not initialized. Check GEMINI_API_KEY.")

        try:
            # Gemini expects image part
            if isinstance(image_data, bytes):
                # google-genai client handles bytes/Part object
                image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)
            else:
                # If it's pure base64 string, might need conversion, but usually passed as bytes
                # Assume bytes for now as standard internal format
                import base64
                if isinstance(image_data, str):
                     image_bytes = base64.b64decode(image_data)
                     image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                else:
                     raise ValueError("Invalid image data format")

            # Config
            config = types.GenerateContentConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS,
            )
            
            if response_schema:
                config.response_mime_type = "application/json"
                # Newer genai allows passing schema directly often, but let's stick to prompt + JSON mime type for reliability across versions unless strict schema object is ready.
                # Actually, 0.2.0 client supports `response_schema` if properly typed.
                # For simplicity/robustness with dynamic schemas, we'll force JSON in prompt + mime type.
                pass
            
            final_prompt = prompt
            if response_schema:
                 schema_str = json.dumps(response_schema, indent=2)
                 final_prompt = f"{prompt}\n\nReturn JSON matching this schema:\n{schema_str}"

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        image_part,
                        types.Part.from_text(text=final_prompt)
                    ]
                )
            ]

            # Generate (Using async if available, default client is sync? 
            # google-genai 1.0+ has async. genai.Client behaves... let's check. 
            # Actually, standard python client is sync usually unless using AsyncClient.
            # But the user installed `google-genai`. Let's assume usage of `aio`.
            # If standard `genai.Client` is sync, we might block the loop. 
            # Let's try to use the async version if possible, or wrap it.
            # NOTE: `google-genai` package (the new one) supports `aio`.
            
            response = await self.gemini_client.aio.models.generate_content(
                model=self.gemini_vision_model,
                contents=contents,
                config=config
            )
            
            response_text = response.text
             
            if response_schema:
                return self._extract_first_json_object(response_text)
                
            return response_text

        except Exception as e:
            logger.error(f"Gemini vision error: {e}")
            if "429" in str(e):
                raise RateLimitError("Gemini Rate Limit Exceeded")
            raise LLMError(f"Gemini vision error: {e}")

    # -----------------------------------------------------
    # Compatibility Methods
    # -----------------------------------------------------
    async def classify_initial_message(self, text: str) -> Dict[str, str]:
        """
        Specific workflow method - implemented using Groq
        """
        from pathlib import Path
        try:
            # We need to manually load the prompt here since we are inside the class
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
gemini_service = HybridLLMService()
# Also expose as generic name
llm_service = gemini_service
