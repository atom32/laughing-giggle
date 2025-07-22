"""
Authentication API endpoints for user registration, login, and logout
"""
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_async_session
from app.core.middleware import get_current_active_user, security
from app.models.user import User
from app.schemas.auth import (
    UserRegistrationRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    LogoutResponse,
    ErrorResponse,
    PasswordChangeRequest
)
from app.services.auth_service import AuthService

router = APIRouter()
settings = get_settings()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Create a new user account with username and password. Returns access token upon successful registration.",
    responses={
        201: {"description": "User registered successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        409: {"model": ErrorResponse, "description": "Username already exists"},
    }
)
async def register(
    user_data: UserRegistrationRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)]
) -> TokenResponse:
    """
    Register a new user account.
    
    Args:
        user_data: User registration data (username and password)
        db: Database session
        
    Returns:
        TokenResponse: Access token and user information
        
    Raises:
        HTTPException: If registration fails due to validation or username conflict
    """
    auth_service = AuthService(db)
    
    try:
        # Attempt to register the user
        user = await auth_service.register_user(
            username=user_data.username,
            password=user_data.password
        )
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and get access token",
    description="Authenticate user with username and password. Returns access token upon successful login.",
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        400: {"model": ErrorResponse, "description": "Invalid input data"},
    }
)
async def login(
    user_data: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_async_session)]
) -> TokenResponse:
    """
    Authenticate user and return access token.
    
    Args:
        user_data: User login credentials (username and password)
        db: Database session
        
    Returns:
        TokenResponse: Access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            username=user_data.username,
            password=user_data.password
        )
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = auth_service.create_access_token(user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout user and invalidate token",
    description="Logout the current user and invalidate their access token.",
    responses={
        200: {"description": "Logout successful"},
        401: {"model": ErrorResponse, "description": "Invalid or missing token"},
    }
)
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_async_session)]
) -> LogoutResponse:
    """
    Logout user and invalidate token.
    
    Args:
        credentials: HTTP Bearer credentials containing JWT token
        db: Database session
        
    Returns:
        LogoutResponse: Logout confirmation message
        
    Raises:
        HTTPException: If token is invalid
    """
    auth_service = AuthService(db)
    
    try:
        # Verify token is valid before revoking
        user = await auth_service.verify_token(credentials.credentials)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Revoke the token (placeholder implementation)
        await auth_service.revoke_token(credentials.credentials)
        
        return LogoutResponse(message="Successfully logged out")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed due to server error"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information",
    description="Get information about the currently authenticated user.",
    responses={
        200: {"description": "User information retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Invalid or missing token"},
    }
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user information
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Refresh the current access token to extend session.",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"model": ErrorResponse, "description": "Invalid or expired token"},
    }
)
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_async_session)]
) -> TokenResponse:
    """
    Refresh access token.
    
    Args:
        credentials: HTTP Bearer credentials containing current JWT token
        db: Database session
        
    Returns:
        TokenResponse: New access token and user information
        
    Raises:
        HTTPException: If token refresh fails
    """
    auth_service = AuthService(db)
    
    try:
        # Verify current token and get user
        user = await auth_service.verify_token(credentials.credentials)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        new_token = auth_service.create_access_token(user)
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed due to server error"
        )


@router.post(
    "/change-password",
    response_model=LogoutResponse,
    summary="Change user password",
    description="Change the password for the currently authenticated user.",
    responses={
        200: {"description": "Password changed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid password data"},
        401: {"model": ErrorResponse, "description": "Invalid current password or token"},
    }
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)]
) -> LogoutResponse:
    """
    Change user password.
    
    Args:
        password_data: Old and new password data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        LogoutResponse: Password change confirmation
        
    Raises:
        HTTPException: If password change fails
    """
    auth_service = AuthService(db)
    
    try:
        success = await auth_service.change_password(
            user_id=current_user.id,
            old_password=password_data.old_password,
            new_password=password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        return LogoutResponse(message="Password changed successfully")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed due to server error"
        )