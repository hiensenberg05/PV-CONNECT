"""
LLM Service using Google Gemini (Flash)
Optimized for LangGraph + FastAPI with strict rate-limit handling
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


# =========================================================
# Custom Exceptions
# =========================================================

class RateLimitError(Exception):
    """Raised when Gemini API quota or rate limit (429) is hit"""
    pass


# =========================================================
# Gemini Service
# =========================================================

class GeminiService:
    """Service wrapper for Google Gemini models"""

    def __init__(self):
        # Configure Gemini once
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Initialize models ONCE
        self.text_model = genai.GenerativeModel(settings.GEMINI_TEXT_MODEL)
        self.vision_model = genai.GenerativeModel(settings.GEMINI_VISION_MODEL)

        # Shared generation config
        self.generation_config = {
            "temperature": settings.GEMINI_TEMPERATURE,
            "max_output_tokens": settings.GEMINI_MAX_TOKENS,
        }

        logger.info(
            f"GeminiService initialized | "
            f"text_model={settings.GEMINI_TEXT_MODEL}, "
            f"vision_model={settings.GEMINI_VISION_MODEL}"
        )

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
        Generate text from Gemini.
        Raises RateLimitError on quota exhaustion.
        """
        try:
            full_prompt = (
                f"{system_instruction}\n\n{prompt}"
                if system_instruction else prompt
            )

            config = self.generation_config.copy()
            if response_schema:
                config["response_mime_type"] = "application/json"
                config["response_schema"] = response_schema

            response = await self.text_model.generate_content_async(
                full_prompt,
                generation_config=config
            )

            return response.text

        except Exception as e:
            msg = str(e).lower()
            if "429" in msg or "quota" in msg or "resource exhausted" in msg:
                logger.error(f"Gemini rate limit hit: {e}")
                raise RateLimitError(str(e))

            logger.error(f"Gemini text generation error: {e}")
            raise

    # -----------------------------------------------------
    # Vision / OCR Extraction
    # -----------------------------------------------------
    async def extract_from_image(
        self,
        image_data: bytes,
        prompt: str,
        mime_type: str = "image/jpeg"
    ) -> str:
        """
        Extract structured information from image using Gemini Vision.
        """
        try:
            image_part = {
                "mime_type": mime_type,
                "data": image_data
            }

            response = await self.vision_model.generate_content_async(
                [prompt, image_part],
                generation_config=self.generation_config
            )

            return response.text

        except Exception as e:
            msg = str(e).lower()
            if "429" in msg or "quota" in msg or "resource exhausted" in msg:
                logger.error(f"Gemini vision rate limit hit: {e}")
                raise RateLimitError(str(e))

            logger.error(f"Gemini vision extraction error: {e}")
            raise

    # -----------------------------------------------------
    # Combined Initial Classification (LANG + USER TYPE)
    # -----------------------------------------------------
    async def classify_initial_message(self, text: str) -> Dict[str, str]:
        """
        SINGLE Gemini call to:
        - Detect language (ISO 639-1)
        - Classify user type (patient | doctor)
        """

        try:
            # Load shared classification prompt
            prompt_path = (
                Path(__file__).parent.parent
                / "shared_prompts"
                / "initial_classification.txt"
            )

            system_prompt = prompt_path.read_text(encoding="utf-8")

            # Force JSON output
            config = self.generation_config.copy()
            config["response_mime_type"] = "application/json"

            response = await self.text_model.generate_content_async(
                f"{system_prompt}\n\nUser message:\n{text}",
                generation_config=config
            )

            cleaned = response.text.strip()

            # Safety cleanup (should not happen in JSON mode, but defensive)
            if cleaned.startswith("```"):
                cleaned = (
                    cleaned.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            data = json.loads(cleaned)

            language = data.get("language", settings.DEFAULT_LANGUAGE)
            user_type = data.get("user_type", "patient")

            # Validate language
            if language not in settings.SUPPORTED_LANGUAGES:
                language = settings.DEFAULT_LANGUAGE

            # Validate user type
            if user_type not in ["patient", "doctor"]:
                user_type = "patient"

            logger.info(
                f"Initial classification → language={language}, user_type={user_type}"
            )

            return {
                "language": language,
                "user_type": user_type
            }

        except RateLimitError:
            # Bubble up to LangGraph for graceful stop
            raise

        except Exception as e:
            logger.error(f"Initial classification failed: {e}")
            return {
                "language": settings.DEFAULT_LANGUAGE,
                "user_type": "patient"
            }


# =========================================================
# Singleton Instance (IMPORTANT)
# =========================================================

gemini_service = GeminiService()
