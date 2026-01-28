from pydantic import BaseModel, Field
from typing import Optional, Literal


class User(BaseModel):
    """
    Represents a user interacting with the system.
    """

    phone_number: str
    user_type: Literal["patient", "doctor"]

    name: Optional[str] = None
    email: Optional[str] = None

    is_verified: bool = False

    class Config:
        orm_mode = True
