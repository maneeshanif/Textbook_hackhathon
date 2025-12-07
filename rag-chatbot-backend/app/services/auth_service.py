"""
Authentication service layer.
Handles business logic for authentication operations.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from fastapi import Request

from app.repositories.auth_repository import AuthRepository
from app.services.jwt_service import jwt_service
from app.services.password_service import password_service
from app.models.auth_models import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
    UserDB
)
from app.config import settings
import structlog

logger = structlog.get_logger()


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo
    
    async def signup(
        self,
        signup_data: SignupRequest,
        request: Optional[Request] = None
    ) -> AuthResponse:
        """
        Register a new user and create initial session.
        
        Args:
            signup_data: User registration data
            request: FastAPI request object for logging
        
        Returns:
            AuthResponse with user data and tokens
        
        Raises:
            ValueError: If email already exists or validation fails
        """
        # Check if user already exists
        existing_user = await self.auth_repo.get_user_by_email(signup_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = password_service.hash_password(signup_data.password)
        
        # Create user
        user_db = await self.auth_repo.create_user(
            email=signup_data.email,
            password_hash=password_hash,
            full_name=signup_data.full_name,
            role="user"
        )
        
        # Create tokens
        access_token = jwt_service.create_access_token(
            user_id=user_db.id,
            email=user_db.email,
            role=user_db.role
        )
        
        refresh_token = jwt_service.create_refresh_token(
            user_id=user_db.id,
            remember_me=False
        )
        
        # Store refresh token
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        
        await self.auth_repo.create_refresh_token(
            user_id=user_db.id,
            token=refresh_token,
            expires_at=refresh_expires_at,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        # Log event
        await self.auth_repo.log_auth_event(
            event_type="signup",
            user_id=user_db.id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        logger.info("user_signup_success", user_id=str(user_db.id), email=user_db.email)
        
        return AuthResponse(
            user=UserResponse(**user_db.dict()),
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
    
    async def login(
        self,
        login_data: LoginRequest,
        request: Optional[Request] = None
    ) -> AuthResponse:
        """
        Authenticate user and create session.
        
        Args:
            login_data: Login credentials
            request: FastAPI request object for logging
        
        Returns:
            AuthResponse with user data and tokens
        
        Raises:
            ValueError: If credentials are invalid
        """
        # Get user by email
        user_db = await self.auth_repo.get_user_by_email(login_data.email)
        if not user_db:
            # Log failed attempt
            await self.auth_repo.log_auth_event(
                event_type="failed_login",
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
                metadata={"email": login_data.email, "reason": "user_not_found"}
            )
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not password_service.verify_password(login_data.password, user_db.password_hash):
            # Log failed attempt
            await self.auth_repo.log_auth_event(
                event_type="failed_login",
                user_id=user_db.id,
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
                metadata={"reason": "invalid_password"}
            )
            raise ValueError("Invalid email or password")
        
        # Create tokens
        access_token = jwt_service.create_access_token(
            user_id=user_db.id,
            email=user_db.email,
            role=user_db.role
        )
        
        refresh_token = jwt_service.create_refresh_token(
            user_id=user_db.id,
            remember_me=login_data.remember_me
        )
        
        # Store refresh token
        expire_days = (
            settings.jwt_refresh_token_remember_me_days if login_data.remember_me
            else settings.jwt_refresh_token_expire_days
        )
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=expire_days)
        
        await self.auth_repo.create_refresh_token(
            user_id=user_db.id,
            token=refresh_token,
            expires_at=refresh_expires_at,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        # Log event
        await self.auth_repo.log_auth_event(
            event_type="login",
            user_id=user_db.id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            metadata={"remember_me": login_data.remember_me}
        )
        
        logger.info("user_login_success", user_id=str(user_db.id), email=user_db.email)
        
        return AuthResponse(
            user=UserResponse(**user_db.dict()),
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.jwt_access_token_expire_minutes * 60
        )
    
    async def refresh_access_token(
        self,
        refresh_token: str,
        request: Optional[Request] = None
    ) -> tuple[str, int]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from httpOnly cookie
            request: FastAPI request object for logging
        
        Returns:
            Tuple of (new_access_token, expires_in_seconds)
        
        Raises:
            ValueError: If refresh token is invalid or expired
        """
        # Verify refresh token
        payload = jwt_service.verify_refresh_token(refresh_token)
        if not payload:
            raise ValueError("Invalid or expired refresh token")
        
        user_id = UUID(payload["sub"])
        
        # Verify token exists in database and is not revoked
        token_db = await self.auth_repo.get_refresh_token(refresh_token)
        if not token_db:
            raise ValueError("Refresh token not found or revoked")
        
        # Get user
        user_db = await self.auth_repo.get_user_by_id(user_id)
        if not user_db:
            raise ValueError("User not found")
        
        # Create new access token
        access_token = jwt_service.create_access_token(
            user_id=user_db.id,
            email=user_db.email,
            role=user_db.role
        )
        
        # Log event
        await self.auth_repo.log_auth_event(
            event_type="token_refresh",
            user_id=user_db.id,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        logger.debug("access_token_refreshed", user_id=str(user_db.id))
        
        return access_token, settings.jwt_access_token_expire_minutes * 60
    
    async def logout(
        self,
        refresh_token: str,
        request: Optional[Request] = None
    ) -> None:
        """
        Logout user by revoking refresh token.
        
        Args:
            refresh_token: Refresh token to revoke
            request: FastAPI request object for logging
        """
        # Verify and get user from token
        payload = jwt_service.verify_refresh_token(refresh_token)
        if payload:
            user_id = UUID(payload["sub"])
            
            # Revoke refresh token
            await self.auth_repo.revoke_refresh_token(refresh_token)
            
            # Log event
            await self.auth_repo.log_auth_event(
                event_type="logout",
                user_id=user_id,
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
            
            logger.info("user_logout", user_id=str(user_id))
    
    async def verify_access_token(self, access_token: str) -> Optional[UserDB]:
        """
        Verify access token and return user data.

        Args:
            access_token: JWT access token

        Returns:
            UserDB if valid, None otherwise
        """
        payload = jwt_service.verify_access_token(access_token)
        if not payload:
            return None

        user_id = UUID(payload["sub"])
        user_db = await self.auth_repo.get_user_by_id(user_id)
        return user_db

    async def get_preferences(self, user_id: UUID) -> Optional[dict]:
        """
        Get user preferences.

        Args:
            user_id: User's UUID

        Returns:
            User preferences dict if found, None otherwise
        """
        prefs = await self.auth_repo.get_preferences(user_id)

        # If no preferences exist, create default ones
        if not prefs:
            try:
                prefs = await self.auth_repo.create_preferences(user_id)
                logger.info("default_preferences_created", user_id=str(user_id))
            except Exception as e:
                logger.warning("failed_to_create_default_preferences", user_id=str(user_id), error=str(e))
                return None

        return prefs

    async def update_preferences(
        self,
        user_id: UUID,
        difficulty: Optional[str] = None,
        focus_tags: Optional[list] = None,
        preferred_language: Optional[str] = None,
        last_chapters: Optional[list] = None
    ) -> dict:
        """
        Update user preferences.

        Args:
            user_id: User's UUID
            difficulty: Learning difficulty level
            focus_tags: Topics of interest
            preferred_language: Preferred language (en/ur)
            last_chapters: Recently viewed chapters

        Returns:
            Updated preferences dict
        """
        return await self.auth_repo.update_preferences(
            user_id=user_id,
            difficulty=difficulty,
            focus_tags=focus_tags,
            preferred_language=preferred_language,
            last_chapters=last_chapters
        )

