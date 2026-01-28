import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class CloudinaryService:
    """
    Cloudinary service for media storage.

    Stores:
    - Prescription images
    - Bills
    - Audio files

    Returns ONLY URLs.
    """

    def __init__(self):
        self.enabled = all([
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        ])

        if self.enabled:
            try:
                import cloudinary
                cloudinary.config(
                    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                    api_key=settings.CLOUDINARY_API_KEY,
                    api_secret=settings.CLOUDINARY_API_SECRET
                )
                logger.info("Cloudinary configured")
            except ImportError:
                logger.warning("Cloudinary SDK missing")
                self.enabled = False
        else:
            logger.info("Cloudinary not configured (optional)")

    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str = "pv-connect/uploads"
    ) -> Optional[str]:
        if not self.enabled:
            return None

        try:
            import cloudinary.uploader

            result = cloudinary.uploader.upload(
                file_bytes,
                folder=folder,
                public_id=filename,
                resource_type="auto"
            )

            return result.get("secure_url")

        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            return None

    async def delete_file(self, public_id: str) -> bool:
        if not self.enabled:
            return False

        try:
            import cloudinary.uploader
            res = cloudinary.uploader.destroy(public_id)
            return res.get("result") == "ok"
        except Exception:
            return False


# Singleton
cloudinary_service = CloudinaryService()
