from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request DTOs
class SoalCreateRequest(BaseModel):
    pertanyaan: str = Field(..., min_length=1, description="Question text")
    jawaban_benar: str = Field(..., min_length=1, description="Correct answer")
    dictionary_id: Optional[int] = Field(None, description="Kamus ID reference (optional)")
    sublevel_id: int = Field(..., description="SubLevel ID this question belongs to")
    video_url: Optional[str] = Field(None, description="Video URL for question (optional)")

class SoalUpdateRequest(BaseModel):
    pertanyaan: Optional[str] = Field(None, min_length=1, description="Question text")
    jawaban_benar: Optional[str] = Field(None, min_length=1, description="Correct answer")
    dictionary_id: Optional[int] = Field(None, description="Kamus ID reference")
    sublevel_id: Optional[int] = Field(None, description="SubLevel ID")
    video_url: Optional[str] = Field(None, description="Video URL")

class BulkDeleteSoalRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="List of soal IDs to delete")
    permanent: bool = Field(False, description="Permanent delete (default: soft delete)")
    
class BulkRestoreSoalRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="List of soal IDs to restore")

# Response DTOs
class SoalData(BaseModel):
    id: int
    pertanyaan: str
    jawaban_benar: str
    dictionary_id: Optional[int] = None
    sublevel_id: int
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    
    # Related data
    kamus: Optional[Dict[str, Any]] = None
    sublevel: Optional[Dict[str, Any]] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SoalListData(BaseModel):
    """Simplified data for list views"""
    id: int
    pertanyaan: str
    jawaban_benar: str
    dictionary_word: Optional[str] = None
    sublevel_name: Optional[str] = None
    level_name: Optional[str] = None
    has_video: bool = False
    has_image: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    
    class Config:
        from_attributes = True

class SoalResponse(BaseModel):
    success: bool
    message: str
    data: Optional[SoalData] = None

class SoalListResponse(BaseModel):
    success: bool
    message: str
    data: List[SoalListData]
    pagination: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

class SoalDeleteResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class SoalRestoreResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class SoalStatisticsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Helper DTOs
class AvailableKamusData(BaseModel):
    id: int
    word_text: str
    definition: str
    video_url: Optional[str] = None
    total_soal: int = 0

class AvailableSubLevelData(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    level_id: int
    level_name: Optional[str] = None
    total_soal: int = 0