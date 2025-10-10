from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
# ✅ DTO Enum bisa lowercase untuk user-friendly
class KamusCategoryEnum(str, Enum):
    ALPHABET = "alphabet"
    NUMBERS = "numbers"
    IMBUHAN = "imbuhan"

class KamusCreateRequest(BaseModel):
    """Kamus creation request"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    word_text: str = Field(..., min_length=1, max_length=255)
    definition: str = Field(..., min_length=1)
    category: KamusCategoryEnum = Field(default=KamusCategoryEnum.ALPHABET)
    image_url_ref: Optional[str] = Field(None, max_length=255)
    video_url: Optional[str] = Field(None, max_length=255)
    
    # ✅ Convert lowercase to uppercase for database
    @field_validator('category', mode='before')
    @classmethod
    def convert_category(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v
class KamusUpdateRequest(BaseModel):
    """Kamus update request - all fields optional"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    word_text: Optional[str] = Field(None, min_length=1, max_length=255)
    definition: Optional[str] = Field(None, min_length=1)
    category: Optional[KamusCategoryEnum] = Field(None, description="Kategori kamus")
    image_url_ref: Optional[str] = Field(None, max_length=255)
    video_url: Optional[str] = Field(None, max_length=255)

class KamusResponse(BaseModel):
    """Kamus response"""
    success: bool
    message: str
    data: dict

class KamusListResponse(BaseModel):
    """Kamus list response with pagination"""
    success: bool
    message: str
    data: List[dict]
    pagination: dict