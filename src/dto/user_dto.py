from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Enum untuk role validation
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

# Request DTOs
class UserCreateDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "Password123",
                "nama": "John Doe",
                "telpon": "+628123456789"
            }
        }
    )
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    nama: str = Field(..., min_length=2, max_length=255)
    telpon: Optional[str] = Field(None, max_length=20)

class UserUpdateDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "username": "johndoe_updated",
                "email": "john.updated@example.com",
                "nama": "John Doe Updated",
                "telpon": "+628987654321",
                "bio": "Updated bio",
                "avatar": "avatar_url.jpg"
            }
        }
    )
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    nama: Optional[str] = Field(None, min_length=2, max_length=255)
    telpon: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = None
    avatar: Optional[str] = None

class UserRoleUpdateDTO(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "moderator"
            }
        }
    )
    
    role: UserRoleEnum

# Data DTOs (for response data field)
class UserDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "unique_id": "USR-00001",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "nama": "John Doe",
                "telpon": "+628123456789",
                "role": "user",
                "is_active": True,
                "is_verified": False,
                "avatar": "avatar_url.jpg",
                "bio": "User bio",
                "total_badges": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-01T00:00:00Z"
            }
        }
    )
    
    id: int
    unique_id: str
    username: str
    email: str
    nama: Optional[str] = None
    telpon: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    avatar: Optional[str] = None
    bio: Optional[str] = None
    total_badges: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class UserListDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "unique_id": "USR-00001",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "nama": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": False,
                "total_badges": 5,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    )
    
    id: int
    unique_id: str
    username: str
    email: str
    nama: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    total_badges: int = 0
    created_at: datetime

class UserProfileDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "unique_id": "USR-00001",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "nama": "John Doe",
                "telpon": "+628123456789",
                "role": "user",
                "is_active": True,
                "is_verified": False,
                "avatar": "avatar_url.jpg",
                "bio": "User bio",
                "total_badges": 5,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "last_login": "2024-01-01T00:00:00Z"
            }
        }
    )
    
    id: int
    unique_id: str
    username: str
    email: str
    nama: Optional[str] = None
    telpon: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    avatar: Optional[str] = None
    bio: Optional[str] = None
    total_badges: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

# Response Wrapper DTOs
class UserResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "User retrieved successfully",
                "data": {
                    "id": 1,
                    "unique_id": "USR-00001",
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "nama": "John Doe",
                    "role": "user",
                    "is_active": True,
                    "is_verified": False,
                    "total_badges": 5
                }
            }
        }
    )
    
    success: bool
    message: str
    data: UserDataDTO

class UserListResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Users retrieved successfully",
                "data": [
                    {
                        "id": 1,
                        "unique_id": "USR-00001",
                        "username": "johndoe",
                        "email": "john.doe@example.com",
                        "nama": "John Doe",
                        "role": "user",
                        "is_active": True,
                        "is_verified": False,
                        "total_badges": 5,
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }
    )
    
    success: bool
    message: str
    data: List[UserListDataDTO]

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Profile retrieved successfully",
                "data": {
                    "id": 1,
                    "unique_id": "USR-00001",
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "nama": "John Doe",
                    "telpon": "+628123456789",
                    "role": "user",
                    "is_active": True,
                    "is_verified": False,
                    "avatar": "avatar_url.jpg",
                    "bio": "User bio",
                    "total_badges": 5
                }
            }
        }
    )
    
    success: bool
    message: str
    data: UserProfileDataDTO

class UserStatsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "User statistics retrieved successfully",
                "data": {
                    "total_users": 100,
                    "active_users": 85,
                    "verified_users": 70,
                    "inactive_users": 15,
                    "unverified_users": 30,
                    "recent_registrations": 12,
                    "roles": {
                        "admin": 2,
                        "moderator": 5,
                        "user": 93
                    }
                }
            }
        }
    )
    
    success: bool
    message: str
    data: Dict[str, Any]

class GenericUserResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {
                    "user_id": 1,
                    "username": "johndoe",
                    "action": "activated",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            }
        }
    )
    
    success: bool
    message: str
    data: Dict[str, Any]

# Bulk action DTO
class BulkUserActionDTO(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_ids": [1, 2, 3, 4, 5]
            }
        }
    )
    
    user_ids: List[int] = Field(..., min_length=1, max_length=100)

# Backward compatibility aliases
UserResponseDTO = UserDataDTO
UserListResponseDTO = UserListDataDTO
UserProfileDTO = UserProfileDataDTO