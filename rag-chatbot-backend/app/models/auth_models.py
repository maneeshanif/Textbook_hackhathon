"""
Pydantic models for authentication requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


# Request Models

class SignupRequest(BaseModel):
    """Request model for user registration."""
    model_config = ConfigDict(populate_by_name=True)  # Pydantic v2 syntax

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name", alias="fullName")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password has uppercase, lowercase, and number."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class LoginRequest(BaseModel):
    """Request model for user login."""
    model_config = ConfigDict(populate_by_name=True)  # Pydantic v2 syntax

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    remember_me: bool = Field(default=False, description="Extend refresh token lifetime to 30 days", alias="rememberMe")


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    # Refresh token comes from httpOnly cookie, no body needed
    pass


# Response Models

class UserResponse(BaseModel):
    """Response model for user data."""
    id: UUID
    email: str
    full_name: Optional[str]
    role: str
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response model for JWT tokens."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds until access token expires


class AuthResponse(BaseModel):
    """Response model for successful authentication."""
    user: UserResponse
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# Database Models

class UserDB(BaseModel):
    """Database model for users table."""
    id: UUID
    email: str
    password_hash: str
    full_name: Optional[str]
    role: str
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RefreshTokenDB(BaseModel):
    """Database model for refresh_tokens table."""
    id: UUID
    user_id: UUID
    token_hash: str
    device_info: dict
    ip_address: Optional[str]
    user_agent: Optional[str]
    expires_at: datetime
    created_at: datetime
    revoked: bool
    revoked_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AuthEventDB(BaseModel):
    """Database model for auth_events table."""
    id: UUID
    user_id: Optional[UUID]
    event_type: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: dict
    created_at: datetime
    
    class Config:
        from_attributes = True
