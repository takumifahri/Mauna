from pydantic import Field, BaseModel, EmailStr
# Pydantic models for request validation
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "Password123",
                "first_name": "John",
                "last_name": "Doe"
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
