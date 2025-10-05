from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request DTOs
class LevelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Level name")
    description: Optional[str] = Field(None, description="Level description")
    tujuan: Optional[str] = Field(None, description="Level objective")

class LevelUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    tujuan: Optional[str] = Field(None)

class BulkDeleteRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="List of level IDs to delete")
    permanent: bool = Field(False, description="Permanent delete")

class BulkRestoreRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="List of level IDs to restore")

# Response DTOs
class LevelData(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    tujuan: Optional[str] = None
    total_sublevels: int
    is_deleted: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None  # ✅ Make optional
    deleted_at: Optional[datetime] = None  # ✅ Make optional
    
    class Config:
        from_attributes = True  # ✅ Enable ORM mode for SQLAlchemy

class LevelResponse(BaseModel):
    success: bool
    message: str
    data: Optional[LevelData] = None

class LevelListResponse(BaseModel):
    success: bool
    message: str
    data: List[LevelData]
    pagination: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

class LevelDeleteResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class LevelRestoreResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class LevelStatisticsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None