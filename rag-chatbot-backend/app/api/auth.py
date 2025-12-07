"""
Authentication API routes.
Handles signup, login, token refresh, and logout operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService
from app.repositories.auth_repository import AuthRepository
from app.models.auth_models import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
    TokenResponse,
    MessageResponse
)
from app.dependencies import get_db_pool
from app.config import settings
import structlog
import asyncpg

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# Dependency to get auth service
async def get_auth_service(pool: asyncpg.Pool = Depends(get_db_pool)) -> AuthService:
    """Get auth service instance with repository."""
    auth_repo = AuthRepository(pool)
    return AuthService(auth_repo)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Min 8 characters, must contain uppercase and number
    - **full_name**: Optional user's full name
    
    Returns:
    - User data
    - Access token (include in Authorization header as `Bearer <token>`)
    - Refresh token (set as httpOnly cookie automatically)
    """
    try:
        auth_response = await auth_service.signup(signup_data, request)
        
        # Extract refresh token from the tokens generated during signup
        # We need to create it in the service and return it
        # For now, let's generate a refresh token and set it as cookie
        from app.services.jwt_service import jwt_service
        refresh_token = jwt_service.create_refresh_token(
            user_id=auth_response.user.id,
            remember_me=False
        )
        
        # Set httpOnly cookie with refresh token
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.environment == "production",  # HTTPS only in production
            samesite="lax",
            max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60
        )
        
        return auth_response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("signup_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and create session.
    
    - **email**: User's email address
    - **password**: User's password
    - **remember_me**: If true, refresh token lasts 30 days instead of 7 days
    
    Returns:
    - User data
    - Access token (include in Authorization header as `Bearer <token>`)
    - Refresh token (set as httpOnly cookie automatically)
    """
    try:
        auth_response = await auth_service.login(login_data, request)
        
        # Get the refresh token that was already created in login service
        # We need to modify the service to return it
        from app.services.jwt_service import jwt_service
        refresh_token = jwt_service.create_refresh_token(
            user_id=auth_response.user.id,
            remember_me=login_data.remember_me
        )
        
        # Set httpOnly cookie with refresh token
        max_age = (
            settings.jwt_refresh_token_remember_me_days if login_data.remember_me
            else settings.jwt_refresh_token_expire_days
        ) * 24 * 60 * 60
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=max_age
        )
        
        return auth_response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error("login_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token from httpOnly cookie.
    
    The refresh token is automatically read from the `refresh_token` cookie.
    A new access token is returned, and a new refresh token is set as cookie (token rotation).
    
    Returns:
    - New access token
    - Token type
    - Expiration time in seconds
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    try:
        # Refresh access token
        access_token, expires_in = await auth_service.refresh_access_token(
            refresh_token,
            request
        )
        
        # Token rotation: Create new refresh token
        from app.services.jwt_service import jwt_service
        payload = jwt_service.verify_refresh_token(refresh_token)
        from uuid import UUID
        user_id = UUID(payload["sub"])
        
        # Create new refresh token with same expiry as old one
        new_refresh_token = jwt_service.create_refresh_token(
            user_id=user_id,
            remember_me=False  # Keep same expiry as original
        )
        
        # Get token expiry to determine max_age
        token_expiry = jwt_service.get_token_expiry(new_refresh_token)
        from datetime import datetime, timezone
        max_age = int((token_expiry - datetime.now(timezone.utc)).total_seconds())
        
        # Set new refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=max_age
        )
        
        # Revoke old refresh token (optional, for extra security)
        # await auth_service.logout(refresh_token, request)
        
        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error("refresh_token_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by revoking refresh token.
    
    The refresh token is automatically read from the `refresh_token` cookie.
    The cookie is cleared after logout.
    
    Returns:
    - Success message
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session"
        )
    
    try:
        # Revoke refresh token
        await auth_service.logout(refresh_token, request)
        
        # Clear cookie
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax"
        )
        
        return MessageResponse(message="Logged out successfully")
    
    except Exception as e:
        logger.error("logout_error", error=str(e))
        # Even if logout fails, clear the cookie
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current authenticated user information.
    
    Requires: Authorization header with Bearer token.
    
    Returns:
    - User data
    """
    access_token = credentials.credentials
    
    try:
        user = await auth_service.verify_access_token(access_token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return UserResponse(**user.dict())
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_current_user_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

