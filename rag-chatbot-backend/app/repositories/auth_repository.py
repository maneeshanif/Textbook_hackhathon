"""
Repository layer for authentication database operations.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
import hashlib
import asyncpg

from app.models.auth_models import UserDB, RefreshTokenDB, AuthEventDB
import structlog

logger = structlog.get_logger()


class AuthRepository:
    """Repository for authentication-related database operations."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    # User operations
    
    async def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None,
        role: str = "user"
    ) -> UserDB:
        """Create a new user in the database."""
        query = """
            INSERT INTO users (email, password_hash, full_name, role, email_verified, created_at, updated_at)
            VALUES ($1, $2, $3, $4, FALSE, NOW(), NOW())
            RETURNING id, email, password_hash, full_name, role, email_verified, created_at, updated_at
        """
        
        try:
            row = await self.db_pool.fetchrow(query, email, password_hash, full_name, role)
            logger.info("user_created", user_id=str(row['id']), email=email)
            return UserDB(**dict(row))
        except asyncpg.UniqueViolationError:
            logger.warning("user_creation_failed_duplicate_email", email=email)
            raise ValueError(f"User with email {email} already exists")
    
    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email address."""
        query = """
            SELECT id, email, password_hash, full_name, role, email_verified, created_at, updated_at
            FROM users
            WHERE email = $1
        """
        
        row = await self.db_pool.fetchrow(query, email)
        if row:
            return UserDB(**dict(row))
        return None
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserDB]:
        """Get user by ID."""
        query = """
            SELECT id, email, password_hash, full_name, role, email_verified, created_at, updated_at
            FROM users
            WHERE id = $1
        """
        
        row = await self.db_pool.fetchrow(query, user_id)
        if row:
            return UserDB(**dict(row))
        return None
    
    async def update_user_email_verified(self, user_id: UUID, verified: bool = True) -> None:
        """Update user's email verification status."""
        query = """
            UPDATE users
            SET email_verified = $1, updated_at = NOW()
            WHERE id = $2
        """
        await self.db_pool.execute(query, verified, user_id)
        logger.info("user_email_verified", user_id=str(user_id))
    
    # Refresh token operations
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token using SHA-256 for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def create_refresh_token(
        self,
        user_id: UUID,
        token: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[dict] = None
    ) -> RefreshTokenDB:
        """Store a refresh token in the database."""
        token_hash = self.hash_token(token)
        device_info = device_info or {}
        
        query = """
            INSERT INTO refresh_tokens (user_id, token_hash, device_info, ip_address, user_agent, expires_at, created_at, revoked)
            VALUES ($1, $2, $3, $4, $5, $6, NOW(), FALSE)
            RETURNING id, user_id, token_hash, device_info, ip_address, user_agent, expires_at, created_at, revoked, revoked_at
        """
        
        row = await self.db_pool.fetchrow(
            query,
            user_id,
            token_hash,
            device_info,
            ip_address,
            user_agent,
            expires_at
        )
        
        logger.info("refresh_token_created", user_id=str(user_id))
        return RefreshTokenDB(**dict(row))
    
    async def get_refresh_token(self, token: str) -> Optional[RefreshTokenDB]:
        """Get refresh token by token value."""
        token_hash = self.hash_token(token)
        
        query = """
            SELECT id, user_id, token_hash, device_info, ip_address, user_agent, expires_at, created_at, revoked, revoked_at
            FROM refresh_tokens
            WHERE token_hash = $1 AND revoked = FALSE AND expires_at > NOW()
        """
        
        row = await self.db_pool.fetchrow(query, token_hash)
        if row:
            return RefreshTokenDB(**dict(row))
        return None
    
    async def revoke_refresh_token(self, token: str) -> bool:
        """Revoke a refresh token."""
        token_hash = self.hash_token(token)
        
        query = """
            UPDATE refresh_tokens
            SET revoked = TRUE, revoked_at = NOW()
            WHERE token_hash = $1 AND revoked = FALSE
            RETURNING id
        """
        
        row = await self.db_pool.fetchrow(query, token_hash)
        if row:
            logger.info("refresh_token_revoked", token_id=str(row['id']))
            return True
        return False
    
    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user (used during logout all devices)."""
        query = """
            UPDATE refresh_tokens
            SET revoked = TRUE, revoked_at = NOW()
            WHERE user_id = $1 AND revoked = FALSE
            RETURNING id
        """
        
        rows = await self.db_pool.fetch(query, user_id)
        count = len(rows)
        logger.info("all_user_tokens_revoked", user_id=str(user_id), count=count)
        return count
    
    async def cleanup_expired_tokens(self) -> int:
        """Delete expired refresh tokens (cleanup job)."""
        query = """
            DELETE FROM refresh_tokens
            WHERE expires_at < NOW()
            RETURNING id
        """

        rows = await self.db_pool.fetch(query)
        count = len(rows)
        if count > 0:
            logger.info("expired_tokens_cleaned_up", count=count)
        return count

    # User preferences operations

    async def get_preferences(self, user_id: UUID) -> Optional[dict]:
        """Get user preferences by user ID."""
        query = """
            SELECT id, user_id, difficulty, focus_tags, preferred_language, last_chapters, created_at, updated_at
            FROM user_preferences
            WHERE user_id = $1
        """

        row = await self.db_pool.fetchrow(query, user_id)
        if row:
            return dict(row)
        return None

    async def create_preferences(
        self,
        user_id: UUID,
        difficulty: str = "beginner",
        focus_tags: list = None,
        preferred_language: str = "en",
        last_chapters: list = None
    ) -> dict:
        """Create default preferences for a new user."""
        focus_tags = focus_tags or []
        last_chapters = last_chapters or []

        query = """
            INSERT INTO user_preferences (user_id, difficulty, focus_tags, preferred_language, last_chapters, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
            RETURNING id, user_id, difficulty, focus_tags, preferred_language, last_chapters, created_at, updated_at
        """

        row = await self.db_pool.fetchrow(query, user_id, difficulty, focus_tags, preferred_language, last_chapters)
        logger.info("user_preferences_created", user_id=str(user_id))
        return dict(row)

    async def update_preferences(
        self,
        user_id: UUID,
        difficulty: Optional[str] = None,
        focus_tags: Optional[list] = None,
        preferred_language: Optional[str] = None,
        last_chapters: Optional[list] = None
    ) -> dict:
        """Update user preferences."""
        # Build dynamic update query based on provided fields
        updates = []
        values = []
        param_count = 1

        if difficulty is not None:
            updates.append(f"difficulty = ${param_count}")
            values.append(difficulty)
            param_count += 1

        if focus_tags is not None:
            updates.append(f"focus_tags = ${param_count}")
            values.append(focus_tags)
            param_count += 1

        if preferred_language is not None:
            updates.append(f"preferred_language = ${param_count}")
            values.append(preferred_language)
            param_count += 1

        if last_chapters is not None:
            updates.append(f"last_chapters = ${param_count}")
            values.append(last_chapters)
            param_count += 1

        if not updates:
            # No updates provided, just return existing preferences
            return await self.get_preferences(user_id)

        updates.append("updated_at = NOW()")
        values.append(user_id)

        query = f"""
            UPDATE user_preferences
            SET {', '.join(updates)}
            WHERE user_id = ${param_count}
            RETURNING id, user_id, difficulty, focus_tags, preferred_language, last_chapters, created_at, updated_at
        """

        row = await self.db_pool.fetchrow(query, *values)
        if row:
            logger.info("user_preferences_updated", user_id=str(user_id))
            return dict(row)

        raise ValueError(f"Preferences not found for user {user_id}")

    # Auth event logging
    
    async def log_auth_event(
        self,
        event_type: str,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """Log an authentication event for audit purposes."""
        metadata = metadata or {}
        
        query = """
            INSERT INTO auth_events (user_id, event_type, ip_address, user_agent, metadata, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
        """
        
        await self.db_pool.execute(query, user_id, event_type, ip_address, user_agent, metadata)
        logger.debug("auth_event_logged", event_type=event_type, user_id=str(user_id) if user_id else None)
