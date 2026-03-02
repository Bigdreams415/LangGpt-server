from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
import re


# Signup schema

class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Chukwuemeka Obi"])
    username: str = Field(..., min_length=3, max_length=50, examples=["chukwuemeka_99"])
    email: EmailStr = Field(..., examples=["chukwuemeka@email.com"])
    password: str = Field(..., min_length=8, max_length=128)
    date_of_birth: Optional[str] = Field(None, examples=["15/08/1995"])
    country: Optional[str] = Field(None, max_length=100, examples=["Nigeria"])
    selected_language: Optional[str] = Field(None, examples=["Igbo"])
    level: Optional[str] = Field("beginner", examples=["beginner"])

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        if v[0].isdigit():
            raise ValueError("Username cannot start with a number")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Full name can only contain letters, spaces, hyphens, and apostrophes")
        return v

    @field_validator("selected_language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid = ["Igbo", "Yoruba", "Hausa"]
            if v not in valid:
                raise ValueError(f"Language must be one of: {', '.join(valid)}")
        return v

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid = ["beginner", "intermediate", "advanced"]
            if v not in valid:
                raise ValueError(f"Level must be one of: {', '.join(valid)}")
        return v


# Login schema

class LoginRequest(BaseModel):
    """Accepts either email or username in the identifier field."""
    identifier: str = Field(..., examples=["chukwuemeka@email.com"], description="Email address or username")
    password: str = Field(..., min_length=1)


# Google OAuth schema

class GoogleAuthRequest(BaseModel):
    """
    The Flutter app sends the Google ID token after Google Sign-In.
    We verify it on the backend.
    """
    id_token: str = Field(..., description="Google ID token from Flutter Google Sign-In")
    selected_language: Optional[str] = None
    level: Optional[str] = "beginner"


# Token response models

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# User response model

class UserResponse(BaseModel):
    id: UUID
    full_name: str
    username: str
    email: str
    date_of_birth: Optional[str] = None
    country: Optional[str] = None
    avatar_url: Optional[str] = None
    selected_language: Optional[str] = None
    level: Optional[str] = None
    auth_provider: str
    is_verified: bool
    streak_count: int
    total_xp: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Combined auth + user data — returned on login/signup."""
    user: UserResponse
    tokens: TokenResponse
    is_new_user: bool = False  # True on first signup (for onboarding flow)


# Profile update schema

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    date_of_birth: Optional[str] = None
    country: Optional[str] = None
    selected_language: Optional[str] = None
    level: Optional[str] = None


# Password change schema

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one number")
        return v


class MessageResponse(BaseModel):
    message: str
    success: bool = True