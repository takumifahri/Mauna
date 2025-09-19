from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database import get_db
from ..config.middleware import get_current_user, auth_manager
from ..handler.auth.Authhandler import auth_handler  # Keep existing auth_handler
from ..dto.auth_dto import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    AuthResponse, RegisterResponse, ProfileResponse, LogoutResponse, VerifyResponse
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
async def register(
    register_data: RegisterRequest, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Register a new user - no token given, must login separately"""
    return await auth_handler.register(
        username=register_data.username,
        email=register_data.email,
        password=register_data.password,
        nama=register_data.nama,
        db=db
    )

@router.post("/login", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def login(
    login_data: LoginRequest, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Log in a user and return access token"""
    return await auth_handler.login(
        email_or_username=login_data.email_or_username,
        password=login_data.password,
        db=db
    )

@router.post("/logout", status_code=status.HTTP_200_OK, response_model=LogoutResponse)
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Logout current user"""
    return await auth_handler.logout(current_user, db)

@router.get("/profile", status_code=status.HTTP_200_OK, response_model=ProfileResponse)
async def get_profile(
    request: Request,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current user profile - requires authentication"""
    return await auth_handler.get_profile(current_user)

@router.get("/verify", status_code=status.HTTP_200_OK, response_model=VerifyResponse)
async def verify_token(
    request: Request,
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Verify if token is valid and user is authenticated"""
    return await auth_handler.verify_auth(current_user)

@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Refresh access token"""
    return await auth_handler.refresh_token(refresh_data.token, db)