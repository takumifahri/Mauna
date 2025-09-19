# Auth DTOs
from .auth_dto import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    UserDataResponse,
    UserDataRegisterResponse,
    AuthResponse,
    RegisterResponse,
    ProfileResponse,
    LogoutResponse,
    VerifyResponse
)

# User DTOs
from .user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserRoleUpdateDTO,
    UserResponseDTO,
    UserListResponseDTO,
    UserProfileDTO
)

# Badge DTOs
from .badges_dto import (
    BadgeCreateDTO,
    BadgeResponseDTO,
    UserBadgeDTO,
    UserWithBadgesDTO
)

__all__ = [
    # Auth DTOs
    "RegisterRequest",
    "LoginRequest", 
    "RefreshTokenRequest",
    "UserDataResponse",
    "UserDataRegisterResponse",
    "AuthResponse",
    "RegisterResponse",
    "ProfileResponse",
    "LogoutResponse",
    "VerifyResponse",
    
    # User DTOs
    "UserCreateDTO",
    "UserUpdateDTO",
    "UserRoleUpdateDTO",
    "UserResponseDTO",
    "UserListResponseDTO",
    "UserProfileDTO",
    
    # Badge DTOs
    "BadgeCreateDTO",
    "BadgeResponseDTO",
    "UserBadgeDTO",
    "UserWithBadgesDTO"
]