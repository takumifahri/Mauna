from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BadgeCreateDTO(BaseModel):
    nama: str = Field(..., min_length=3, max_length=255)
    deskripsi: Optional[str] = None
    icon: Optional[str] = None
    level: str = Field(default="easy", pattern=r"^(easy|medium|hard)$")  # Ubah pattern ke regex

class BadgeResponseDTO(BaseModel):
    id: int
    nama: str
    deskripsi: Optional[str]
    icon: Optional[str]
    level: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBadgeDTO(BaseModel):
    badge_id: int
    nama: str
    level: str
    earned_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserWithBadgesDTO(BaseModel):
    id: int
    username: str
    email: str
    nama: Optional[str]
    total_badges: int
    badges: List[UserBadgeDTO]
    
    class Config:
        from_attributes = True