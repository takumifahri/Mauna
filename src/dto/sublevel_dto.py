from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime

# Request DTOs
class SubLevelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="SubLevel name")
    description: Optional[str] = Field(None, description="SubLevel description")
    tujuan: Optional[str] = Field(None, description="SubLevel objective")
    level_id: int = Field(..., description="Parent level ID")

class SubLevelUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    tujuan: Optional[str] = Field(None)
    level_id: Optional[int] = Field(None)

class BulkDeleteRequest(BaseModel):
    ids: Annotated[List[int], Field(min_length=1, description="List of sublevel IDs to delete")]
    permanent: bool = Field(False, description="Permanent delete")

class BulkRestoreRequest(BaseModel):
    ids: Annotated[List[int], Field(min_length=1, description="List of sublevel IDs to restore")]

# Response DTOs
class SubLevelData(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    tujuan: Optional[str] = None
    level_id: int
    level_name: Optional[str] = None
    total_soal: int
    is_deleted: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None  # ✅ Make optional
    deleted_at: Optional[datetime] = None  # ✅ Make optional
    
    class Config:
        from_attributes = True  # ✅ Enable ORM mode for SQLAlchemy

class SubLevelResponse(BaseModel):
    success: bool
    message: str
    data: Optional[SubLevelData] = None

class SubLevelListResponse(BaseModel):
    success: bool
    message: str
    data: List[SubLevelData]
    pagination: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None

class SubLevelDeleteResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class SubLevelRestoreResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class SubLevelStatisticsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None