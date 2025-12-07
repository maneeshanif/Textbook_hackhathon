"""
Authentication service for Better Auth integration.

Handles user registration, login, session management, and preferences.
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import asyncpg
import structlog

from app.models.auth import (
    UserCreate,
    UserResponse,
    UserPreferences,
    UserPreferencesResponse,
    AuthResponse,
    Session,
)

logger = structlog.get_logger()


class AuthService:
    """Authentication and user management service"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.session_duration = timedelta(days=30)  # 30 days session

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256 (replace with bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(32)

    async def signup(
        self,
        user_data: UserCreate,
        preferences: Optional[UserPreferences] = None
    ) -> AuthResponse:
        """
        Register new user and create initial session.
        
        Args:
            user_data: User registration data
            preferences: Optional initial preferences
            
        Returns:
            AuthResponse with user info and session token
            
        Raises:
            ValueError: If email already exists
        """
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                # Check if user exists
                existing = await conn.fetchrow(
                    "SELECT id FROM users WHERE email = $1",
                    user_data.email
                )
                if existing:
                    raise ValueError("Email already registered")

                # Create user
                password_hash = self._hash_password(user_data.password)
                user_row = await conn.fetchrow(
                    """
                    INSERT INTO users (email, name, email_verified)
                    VALUES ($1, $2, FALSE)
                    RETURNING id, email, name, email_verified, created_at
                    """,
                    user_data.email,
                    user_data.name,
                )

                user_id = user_row["id"]

                # Store password hash (in production, use accounts table with better-auth provider)
                await conn.execute(
                    """
                    INSERT INTO accounts (user_id, provider, provider_account_id, access_token)
                    VALUES ($1, 'credentials', $2, $3)
                    """,
                    user_id,
                    user_data.email,
                    password_hash,
                )

                # Create default preferences
                prefs = preferences or UserPreferences()
                await conn.execute(
                    """
                    INSERT INTO user_preferences (
                        user_id, difficulty, focus_tags, preferred_language, last_chapters
                    )
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    user_id,
                    prefs.difficulty,
                    prefs.focus_tags,
                    prefs.preferred_language,
                    prefs.last_chapters,
                )

                # Create session
                session_token = self._generate_session_token()
                expires_at = datetime.utcnow() + self.session_duration
                await conn.execute(
                    """
                    INSERT INTO auth_sessions (user_id, session_token, expires_at)
                    VALUES ($1, $2, $3)
                    """,
                    user_id,
                    session_token,
                    expires_at,
                )

                logger.info("user_signup", user_id=str(user_id), email=user_data.email)

                return AuthResponse(
                    user=UserResponse(**dict(user_row)),
                    session_token=session_token,
                    expires_at=expires_at,
                )

    async def login(self, email: str, password: str) -> AuthResponse:
        """
        Authenticate user and create session.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            AuthResponse with user info and session token
            
        Raises:
            ValueError: If credentials are invalid
        """
        async with self.db_pool.acquire() as conn:
            # Get user and password hash
            row = await conn.fetchrow(
                """
                SELECT u.id, u.email, u.name, u.email_verified, u.created_at,
                       a.access_token as password_hash
                FROM users u
                JOIN accounts a ON u.id = a.user_id
                WHERE u.email = $1 AND a.provider = 'credentials'
                """,
                email,
            )

            if not row:
                raise ValueError("Invalid credentials")

            # Verify password
            password_hash = self._hash_password(password)
            if password_hash != row["password_hash"]:
                raise ValueError("Invalid credentials")

            user_id = row["id"]

            # Create new session
            session_token = self._generate_session_token()
            expires_at = datetime.utcnow() + self.session_duration
            await conn.execute(
                """
                INSERT INTO auth_sessions (user_id, session_token, expires_at)
                VALUES ($1, $2, $3)
                """,
                user_id,
                session_token,
                expires_at,
            )

            logger.info("user_login", user_id=str(user_id), email=email)

            return AuthResponse(
                user=UserResponse(
                    id=row["id"],
                    email=row["email"],
                    name=row["name"],
                    email_verified=row["email_verified"],
                    created_at=row["created_at"],
                ),
                session_token=session_token,
                expires_at=expires_at,
            )

    async def verify_session(self, session_token: str) -> Optional[UserResponse]:
        """
        Verify session token and return user if valid.
        
        Args:
            session_token: Session token to verify
            
        Returns:
            UserResponse if session is valid, None otherwise
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT u.id, u.email, u.name, u.email_verified, u.created_at
                FROM users u
                JOIN auth_sessions s ON u.id = s.user_id
                WHERE s.session_token = $1 AND s.expires_at > NOW()
                """,
                session_token,
            )

            if not row:
                return None

            return UserResponse(**dict(row))

    async def logout(self, session_token: str) -> bool:
        """
        Invalidate session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            True if session was deleted
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM auth_sessions WHERE session_token = $1",
                session_token,
            )
            return result != "DELETE 0"

    async def get_preferences(self, user_id: UUID) -> Optional[UserPreferencesResponse]:
        """Get user preferences"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, difficulty, focus_tags, preferred_language,
                       last_chapters, created_at, updated_at
                FROM user_preferences
                WHERE user_id = $1
                """,
                user_id,
            )

            if not row:
                return None

            return UserPreferencesResponse(**dict(row))

    async def update_preferences(
        self, user_id: UUID, preferences: UserPreferences
    ) -> UserPreferencesResponse:
        """Update user preferences"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE user_preferences
                SET difficulty = $2,
                    focus_tags = $3,
                    preferred_language = $4,
                    last_chapters = $5,
                    updated_at = NOW()
                WHERE user_id = $1
                RETURNING id, user_id, difficulty, focus_tags, preferred_language,
                          last_chapters, created_at, updated_at
                """,
                user_id,
                preferences.difficulty,
                preferences.focus_tags,
                preferences.preferred_language,
                preferences.last_chapters,
            )

            logger.info("preferences_updated", user_id=str(user_id))

            return UserPreferencesResponse(**dict(row))

    async def add_to_history(self, user_id: UUID, chapter_path: str):
        """Add chapter to user's reading history (last 20)"""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE user_preferences
                SET last_chapters = ARRAY_PREPEND($2, last_chapters)[1:20],
                    updated_at = NOW()
                WHERE user_id = $1
                """,
                user_id,
                chapter_path,
            )
