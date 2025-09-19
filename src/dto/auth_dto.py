from pydantic import Field, BaseModel, EmailStr
from typing import Optional

# Request DTOs
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    nama: str = Field(..., min_length=2, max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "Password123",
                "nama": "John Doe",
        
            }
        }

class LoginRequest(BaseModel):
    email_or_username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    
    class Config:
        schema_extra = {
            "example": {
                "email_or_username": "johndoe",
                "password": "Password123"
            }
        }

class RefreshTokenRequest(BaseModel):
    token: str
    
    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

# Response DTOs
class UserDataResponse(BaseModel):
    id: int
    unique_id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    last_login: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserDataRegisterResponse(BaseModel):
    """Response data for registration - no sensitive info"""
    id: int
    unique_id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    next_step: str
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    """Response for login and refresh token"""
    success: bool
    message: str
    access_token: str
    token_type: str
    expires_in: Optional[int] = None
    data: UserDataResponse

class RegisterResponse(BaseModel):
    """Response for registration - no token"""
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