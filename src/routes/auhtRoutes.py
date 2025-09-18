from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator

from ..database import get_db
from ..handler.auth.Authhandler import (
    auth_handler,
    get_current_user,
    get_current_user_bearer,
    get_current_user_from_state,            # <-- new
    require_admin_state,                    # <-- optional for admin-only
    require_moderator_or_admin_state        # <-- optional for mod/admin
)
from ..models.user import User
from ..dto.auth_dto import RegisterRequest, LoginRequest, RefreshTokenRequest

# Create router instance - hapus prefix /api karena sudah di-handle di __init__.py
router = APIRouter(
    prefix="/auth",  # Sekarang akan menjadi /api/auth
    tags=["Authentication"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)

# Routes
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def register(
    register_data: RegisterRequest, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Register a new user and return access token"""
    return await auth_handler.register(
        username=register_data.username,
        email=register_data.email,
        password=register_data.password,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        db=db
    )

@router.post("/login", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
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

@router.post("/logout", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def logout(
    current_user: User = Depends(get_current_user_from_state),  # use middleware-backed dependency
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Logout current user"""
    return await auth_handler.logout(current_user, db)

@router.get("/profile", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def get_profile(
    current_user: User = Depends(get_current_user_from_state)  # protected via middleware
) -> Dict[str, Any]:
    """Get current user profile"""
    return await auth_handler.get_profile(current_user)

@router.get("/verify", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def verify_token(
    current_user: User = Depends(get_current_user_from_state)
) -> Dict[str, Any]:
    """Verify if token is valid and user is authenticated"""
    return await auth_handler.verify_auth(current_user)

@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Refresh access token"""
    return await auth_handler.refresh_token(refresh_data.token, db)
