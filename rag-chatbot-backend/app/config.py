"""
Configuration management using Pydantic Settings.
Loads environment variables and validates configuration.
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database Configuration
    neon_connection_string: str = Field(
        ...,
        description="PostgreSQL connection string for Neon database"
    )
    
    # Vector Database
    qdrant_url: str = Field(
        ...,
        description="Qdrant Cloud instance URL"
    )
    qdrant_api_key: str = Field(
        ...,
        description="Qdrant API key for authentication"
    )
    
    # AI Service
    gemini_api_key: str = Field(
        ...,
        description="Google Gemini API key"
    )
    
    # Better Auth Configuration (optional, for bonus feature)
    better_auth_url: str | None = Field(
        default=None,
        description="Better Auth instance URL"
    )
    better_auth_api_key: str | None = Field(
        default=None,
        description="Better Auth API key"
    )
    
    # Application Configuration
    environment: str = Field(
        default="development",
        description="Environment: development, staging, or production"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host"
    )
    api_port: int = Field(
        default=8000,
        description="API server port"
    )
    
    # Admin API Security
    admin_api_key: str = Field(
        ...,
        description="API key for admin endpoints"
    )
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # JWT Authentication Configuration
    jwt_secret_key: str = Field(
        ...,
        description="Secret key for JWT token signing (min 32 characters)"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithm for JWT encoding"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=15,
        description="Access token expiration time in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    jwt_refresh_token_remember_me_days: int = Field(
        default=30,
        description="Refresh token expiration when 'Remember Me' is enabled"
    )
    
    # Vector Search Configuration
    similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for vector search results"
    )
    max_chunks: int = Field(
        default=5,
        description="Maximum number of chunks to retrieve for RAG"
    )
    
    # Rate Limiting
    rate_limit_anonymous: int = Field(
        default=10,
        description="Requests per minute for anonymous users"
    )
    rate_limit_authenticated: int = Field(
        default=30,
        description="Requests per minute for authenticated users"
    )
    
    # Database Connection Pool
    db_pool_min_size: int = Field(
        default=5,
        description="Minimum database connection pool size"
    )
    db_pool_max_size: int = Field(
        default=20,
        description="Maximum database connection pool size"
    )
    
    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v_upper
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed_envs = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in allowed_envs:
            raise ValueError(f"environment must be one of {allowed_envs}")
        return v_lower


# Global settings instance
settings = Settings()
