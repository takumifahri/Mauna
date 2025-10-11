from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from ..database import get_db
from ..config.middleware import get_current_user, auth_manager
from ..handler.auth.Authhandler import auth_handler
from ..dto.auth_dto import (
    RegisterRequest, LoginRequest, RefreshTokenRequest, UpdatePasswordRequest,
    AuthResponse, RegisterResponse, ProfileResponse, LogoutResponse, 
    VerifyResponse, UpdateProfileResponse
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
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    🔒 Logout user dan revoke JWT token
    
    **Protected endpoint** - Requires valid JWT token
    
    Token yang di-logout akan di-blacklist dan tidak bisa digunakan lagi.
    """
    # ✅ Get token from request state (set by middleware)
    token = getattr(request.state, "jwt_token", None)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token not found in request"
        )
    
    return await auth_handler.logout(current_user, token, db)

@router.post("/logout-all", status_code=status.HTTP_200_OK, response_model=LogoutResponse)
async def logout_all_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    🔒 Logout dari semua devices
    
    **Protected endpoint** - Requires valid JWT token
    """
    return await auth_handler.logout_all_sessions(current_user, db)

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


@router.patch("/profile", status_code=status.HTTP_200_OK, response_model=UpdateProfileResponse)
async def update_profile(
    nama: Optional[str] = Form(None),
    telpon: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),  # ✅ Avatar is optional
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update user profile - all fields optional
    
    Can update:
    - nama: Full name
    - telpon: Phone number
    - bio: User biography
    - username: Username
    - avatar: Profile picture (image file)
    
    Use multipart/form-data to include avatar file
    """
    return await auth_handler.update_profile(
        current_user=current_user,
        nama=nama,
        telpon=telpon,
        bio=bio,
        username=username,
        avatar_file=avatar,
        db=db
    )

@router.delete("/profile/avatar", status_code=status.HTTP_200_OK, response_model=UpdateProfileResponse)
async def delete_avatar(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete user avatar"""
    return await auth_handler.delete_avatar(
        current_user=current_user,
        db=db
    )

@router.put("/profile/password", status_code=status.HTTP_200_OK, response_model=UpdateProfileResponse)
async def change_password(
    password_data: UpdatePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Change user password
    
    Requires:
    - old_password: Current password
    - new_password: New password (must meet strength requirements)
    - confirm_password: Confirm new password
    """
    return await auth_handler.change_password(
        current_user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
        confirm_password=password_data.confirm_password,
        db=db
    )