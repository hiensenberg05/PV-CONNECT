from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    phone_number: str
    user_type: str = "patient"
    name: Optional[str] = None
    license_number: Optional[str] = None
    license_document: Optional[Dict[str, str]] = None
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
