"""
Authentication API endpoints.

Routes:
- POST /api/auth/signup - Register new user
- POST /api/auth/login - Login user
- POST /api/auth/logout - Logout user
- GET /api/auth/me - Get current user
- GET /api/auth/preferences - Get user preferences
- PUT /api/auth/preferences - Update user preferences
"""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse
from typing import Optional

from app.models.auth import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
    UserPreferences,
    UserPreferencesResponse,
)
from app.services.auth_service import AuthService
from app.dependencies import get_db_pool
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def get_auth_service(db_pool=Depends(get_db_pool)) -> AuthService:
    """Dependency to get auth service"""
    return AuthService(db_pool)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """
    Dependency to get current authenticated user from Bearer token.
    
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    session_token = authorization.replace("Bearer ", "")
    user = await auth_service.verify_session(session_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return user


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user account.
    
    Creates user, default preferences, and initial session.
    """
    try:
        auth_response = await auth_service.signup(
            user_data=request,
            preferences=request.preferences
        )
        
        logger.info("signup_success", email=request.email)
        
        return auth_response
    
    except ValueError as e:
        logger.warning("signup_failed", error=str(e), email=request.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("signup_error", error=str(e), email=request.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and create session.
    
    Returns user info and session token on success.
    """
    try:
        auth_response = await auth_service.login(
            email=request.email,
            password=request.password
        )
        
        logger.info("login_success", email=request.email)
        
        return auth_response
    
    except ValueError as e:
        logger.warning("login_failed", error=str(e), email=request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error("login_error", error=str(e), email=request.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by invalidating session.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization header"
        )
    
    session_token = authorization.replace("Bearer ", "")
    success = await auth_service.logout(session_token)
    
    if success:
        logger.info("logout_success")
        return {"message": "Logged out successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires valid Bearer token in Authorization header.
    """
    return current_user


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user's preferences.
    """
    preferences = await auth_service.get_preferences(current_user.id)
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    
    return preferences


@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    preferences: UserPreferences,
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user's preferences.
    """
    try:
        updated = await auth_service.update_preferences(
            user_id=current_user.id,
            preferences=preferences
        )
        
        logger.info("preferences_updated", user_id=str(current_user.id))
        
        return updated
    
    except Exception as e:
        logger.error("preferences_update_error", error=str(e), user_id=str(current_user.id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


@router.post("/history/add")
async def add_chapter_to_history(
    chapter_path: str,
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Add a chapter to user's reading history.
    """
    try:
        await auth_service.add_to_history(current_user.id, chapter_path)
        return {"message": "Chapter added to history"}
    
    except Exception as e:
        logger.error("history_add_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update history"
        )
