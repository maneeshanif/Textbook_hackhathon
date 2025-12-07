"""
JWT token generation and validation service.

Provides functions for creating and verifying access and refresh tokens using PyJWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from uuid import UUID

from app.config import settings
import structlog

logger = structlog.get_logger()


class JWTService:
    """Service for JWT token operations."""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days
        self.refresh_token_remember_me_days = settings.jwt_refresh_token_remember_me_days
    
    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        role: str = "user"
    ) -> str:
        """
        Create a short-lived access token.
        
        Args:
            user_id: User's unique identifier
            email: User's email address
            role: User's role (default: "user")
        
        Returns:
            Encoded JWT access token string
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "access",
            "iat": now,
            "exp": expire
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.debug(
            "access_token_created",
            user_id=str(user_id),
            expires_at=expire.isoformat()
        )
        
        return token
    
    def create_refresh_token(
        self,
        user_id: UUID,
        remember_me: bool = False
    ) -> str:
        """
        Create a long-lived refresh token.
        
        Args:
            user_id: User's unique identifier
            remember_me: If True, extends token lifetime to 30 days
        
        Returns:
            Encoded JWT refresh token string
        """
        now = datetime.now(timezone.utc)
        expire_days = (
            self.refresh_token_remember_me_days if remember_me
            else self.refresh_token_expire_days
        )
        expire = now + timedelta(days=expire_days)
        
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": expire
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.debug(
            "refresh_token_created",
            user_id=str(user_id),
            remember_me=remember_me,
            expires_at=expire.isoformat()
        )
        
        return token
    
    def verify_access_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode an access token.
        
        Args:
            token: JWT access token string
        
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "access":
                logger.warning("invalid_token_type", expected="access", got=payload.get("type"))
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.debug("access_token_expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("invalid_access_token", error=str(e))
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a refresh token.
        
        Args:
            token: JWT refresh token string
        
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "refresh":
                logger.warning("invalid_token_type", expected="refresh", got=payload.get("type"))
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.debug("refresh_token_expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("invalid_refresh_token", error=str(e))
            return None
    
    def decode_token_without_verification(self, token: str) -> Optional[dict]:
        """
        Decode token without verifying signature or expiration.
        Useful for debugging or extracting claims from expired tokens.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload if parseable, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False},
                algorithms=[self.algorithm]
            )
            return payload
        except Exception as e:
            logger.error("token_decode_failed", error=str(e))
            return None
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """
        Extract expiration time from token without full verification.
        
        Args:
            token: JWT token string
        
        Returns:
            Expiration datetime if present, None otherwise
        """
        payload = self.decode_token_without_verification(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        return None


# Global JWT service instance
jwt_service = JWTService()
