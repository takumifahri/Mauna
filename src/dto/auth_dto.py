from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Request DTOs
class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "Password123",
                "nama": "John Doe"
            }
        }
    )
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    nama: str = Field(..., min_length=2, max_length=255)

class UpdateProfileRequest(BaseModel):
    """Update profile request - all fields optional including avatar"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "nama": "John Doe Updated",
                "telpon": "081234567890",
                "bio": "Software Developer at XYZ Company",
                "username": "johndoe_new"
            }
        }
    )
    
    nama: Optional[str] = Field(None, min_length=2, max_length=255, description="Full name")
    telpon: Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    # Avatar will be handled as UploadFile in route, not in this DTO

class UpdatePasswordRequest(BaseModel):
    """Change password request"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "old_password": "OldPassword123",
                "new_password": "NewPassword123",
                "confirm_password": "NewPassword123"
            }
        }
    )
    
    old_password: str = Field(..., min_length=8, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")

class UpdateProfileResponse(BaseModel):
    """Profile update response"""
    success: bool
    message: str
    data: dict
class LoginRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email_or_username": "johndoe",
                "password": "Password123"
            }
        }
    )
    
    email_or_username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)

class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )
    
    token: str

# Response DTOs
class UserDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    unique_id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None

class UserDataRegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    unique_id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    next_step: str = "Please login to get your access token"

class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    data: UserDataResponse

class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: UserDataRegisterResponse

class ProfileResponse(BaseModel):
    success: bool
    message: str
    data: dict

class LogoutResponse(BaseModel):
    success: bool
    message: str
    data: dict

class VerifyResponse(BaseModel):
    success: bool
    message: str
    data: dict