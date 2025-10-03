from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class KamusCreateDTO(BaseModel):
    word_text: str = Field(..., min_length=1, max_length=255)
    definition: str = Field(..., min_length=1)
    video_url: Optional[str] = None
    # Hapus field image dari DTO karena upload via UploadFile
    
class KamusUpdateDTO(BaseModel):
    word_text: Optional[str] = Field(None, min_length=1, max_length=255)
    definition: Optional[str] = Field(None, min_length=1)
    video_url: Optional[str] = None
    # Hapus field image dari DTO karena upload via UploadFile
    
class KamusResponseDTO(BaseModel):
    id: int
    word_text: str
    definition: str
    image_url_ref: Optional[str] = None
    video_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        
class KamusListResponseDTO(BaseModel):
    kamus: List[KamusResponseDTO]
    total: int
    skip: int
    limit: int