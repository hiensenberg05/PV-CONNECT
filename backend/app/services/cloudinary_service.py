import cloudinary
from cloudinary.uploader import upload
from app.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)


def init_cloudinary():
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )


def upload_bytes(data: bytes, folder: str, resource_type: str = "image"):
    init_cloudinary()
    return upload(data, folder=folder, resource_type=resource_type)
