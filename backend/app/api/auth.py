# backend/app/api/auth.py
"""
Authentication API for employee login.
Uses bcrypt for password verification and JWT for tokens.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import bcrypt
import jwt

from app.db.mongo_db import mongodb_service
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# JWT Settings
SECRET_KEY = settings.WHATSAPP_VERIFY_TOKEN or "pv-connect-secret-key-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class Token(BaseModel):
    """Response model for login."""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Request model for login."""
    employee_id: str
    password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate an employee and return a JWT token.
    
    Uses OAuth2PasswordRequestForm for compatibility with existing frontend.
    - username field = employee_id (e.g., EMP001)
    - password field = password
    """
    employee_id = form_data.username.upper()  # Normalize to uppercase
    password = form_data.password
    
    # Find employee in database
    employee = await mongodb_service.db.employees.find_one(
        {"employee_id": employee_id}
    )
    
    if not employee:
        raise HTTPException(
            status_code=401,
            detail="Invalid employee ID or password"
        )
    
    # Check if employee is active
    if not employee.get("active", True):
        raise HTTPException(
            status_code=401,
            detail="Account is disabled. Contact administrator."
        )
    
    # Verify password
    if not verify_password(password, employee["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid employee ID or password"
        )
    
    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": employee_id,
            "name": employee.get("name", "Unknown"),
            "role": employee.get("role", "analyst")
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token)
