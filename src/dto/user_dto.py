from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Request DTOs
class UserRegisterRequestDTO(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLoginRequestDTO(BaseModel):
    email: EmailStr
    password: str

# Response DTOs
class UserRegisterResponseDTO(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

class UserLoginResponseDTO(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    role: str
    token: str

class AuthResponseDTO(BaseModel):
    token: str
    token_type: str = "bearer"

# Base User DTOs
class UserCreateDTO(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserUpdateDTO(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None

class UserDTO(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime