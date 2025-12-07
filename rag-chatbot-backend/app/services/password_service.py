"""
Password hashing and verification service using bcrypt.

Provides secure password hashing with configurable bcrypt rounds.
"""

from passlib.context import CryptContext
import structlog

logger = structlog.get_logger()

# Configure bcrypt with 12 rounds (good balance between security and performance)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class PasswordService:
    """Service for password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain-text password using bcrypt.

        Args:
            password: Plain-text password string

        Returns:
            Bcrypt hashed password string

        Raises:
            ValueError: If password is empty
        """
        if not password:
            raise ValueError("Password cannot be empty")

        # Bcrypt has a 72-byte limit, truncate if necessary
        # Encode to UTF-8 to get byte length
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')

        hashed = pwd_context.hash(password)
        logger.debug("password_hashed")
        return hashed
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a bcrypt hash.
        
        Args:
            plain_password: Plain-text password to verify
            hashed_password: Bcrypt hashed password from database
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)
            logger.debug("password_verification", result=is_valid)
            return is_valid
        except Exception as e:
            logger.warning("password_verification_failed", error=str(e))
            return False
    
    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Check if a hashed password needs to be rehashed.
        Useful when upgrading bcrypt rounds or algorithms.
        
        Args:
            hashed_password: Bcrypt hashed password
        
        Returns:
            True if password should be rehashed, False otherwise
        """
        return pwd_context.needs_update(hashed_password)


# Global password service instance
password_service = PasswordService()
