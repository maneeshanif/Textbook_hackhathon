"""
Authentication models for Better Auth integration.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """User response model (no password)"""
    id: UUID
    email_verified: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UserPreferences(BaseModel):
    """User personalization preferences"""
    difficulty: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    focus_tags: List[str] = Field(default_factory=list)
    preferred_language: str = Field(default="en", pattern="^(en|ur)$")
    last_chapters: List[str] = Field(default_factory=list, max_items=20)


class UserPreferencesResponse(UserPreferences):
    """User preferences with metadata"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Session(BaseModel):
    """Auth session model"""
    id: UUID
    user_id: UUID
    session_token: str
    expires_at: datetime


class LoginRequest(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str


class SignupRequest(UserCreate):
    """Signup with preferences"""
    preferences: Optional[UserPreferences] = None


class AuthResponse(BaseModel):
    """Authentication response"""
    user: UserResponse
    session_token: str
    expires_at: datetime
