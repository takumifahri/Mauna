from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# =====================================================================
# REQUEST DTOs
# =====================================================================

class FinishQuizRequest(BaseModel):
    """Request DTO untuk finish quiz - Simplified"""
    sublevel_id: int = Field(..., description="ID sublevel yang dikerjakan")
    correct_answers: int = Field(..., ge=0, description="Jumlah jawaban benar dari object detection")
    total_score: int = Field(..., ge=0, le=100, description="Total score (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sublevel_id": 1,
                "correct_answers": 4,
                "total_score": 80
            }
        }

class ResetProgressRequest(BaseModel):
    """Request model untuk reset progress"""
    confirm: bool = True

# =====================================================================
# RESPONSE DTOs
# =====================================================================

class SoalResponse(BaseModel):
    """Response model untuk soal individu - Duolingo style"""
    id: int
    question: str
    # ✅ Video dan image URL dari soal untuk object detection
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    
    # ✅ Data dari Kamus (dictionary) - Opsional untuk reference
    dictionary_word: Optional[str] = None
    dictionary_definition: Optional[str] = None
    dictionary_video_url: Optional[str] = None  # Video dari kamus
    dictionary_image_url: Optional[str] = None  # Image dari kamus
    
    # Metadata
    sublevel_name: str
    level_name: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "question": "Tunjukkan isyarat untuk huruf 'A'",
                "video_url": "https://example.com/video.mp4",
                "image_url": "/storage/soal/letter_a.jpg",
                "dictionary_word": "A",
                "dictionary_definition": "Huruf pertama dalam alfabet",
                "dictionary_video_url": "https://example.com/dict_video.mp4",
                "dictionary_image_url": "/storage/kamus/a.jpg",
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner"
            }
        }

class QuizDataResponse(BaseModel):
    """Data quiz yang akan dikirim ke client - Duolingo style"""
    sublevel_id: int
    sublevel_name: str
    sublevel_description: Optional[str] = None
    level_name: str
    total_questions: int
    questions: List[SoalResponse]
    
    # Progress info
    progress_status: str
    is_unlocked: bool
    current_attempt: int
    best_score: int
    best_stars: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "sublevel_id": 1,
                "sublevel_name": "Alphabet A-E",
                "sublevel_description": "Belajar huruf A sampai E dalam bahasa isyarat",
                "level_name": "Beginner",
                "total_questions": 5,
                "questions": [],
                "progress_status": "in_progress",
                "is_unlocked": True,
                "current_attempt": 1,
                "best_score": 0,
                "best_stars": 0
            }
        }

class StartQuizResponse(BaseModel):
    """Response untuk memulai quiz"""
    success: bool
    message: str
    data: QuizDataResponse

class QuizResultResponse(BaseModel):
    """Response DTO setelah finish quiz"""
    score: int = Field(..., description="Score yang didapat")
    correct_answers: int = Field(..., description="Jumlah jawaban benar")
    total_questions: int = Field(..., description="Total soal")
    completion_percentage: int = Field(..., description="Persentase penyelesaian")
    stars: int = Field(..., ge=0, le=3, description="Bintang yang didapat (0-3)")
    status: str = Field(..., description="Status progress")
    attempts: int = Field(..., description="Total percobaan")
    best_score: int = Field(..., description="Score terbaik")
    best_stars: int = Field(..., description="Bintang terbaik")
    is_completed: bool = Field(..., description="Apakah sudah completed")
    next_sublevel_unlocked: bool = Field(..., description="Apakah sublevel/level berikutnya unlocked")
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 80,
                "correct_answers": 4,
                "total_questions": 5,
                "completion_percentage": 80,
                "stars": 2,
                "status": "completed",
                "attempts": 1,
                "best_score": 80,
                "best_stars": 2,
                "is_completed": True,
                "next_sublevel_unlocked": True
            }
        }

class FinishQuizResponse(BaseModel):
    """Response setelah menyelesaikan quiz"""
    success: bool
    message: str
    data: QuizResultResponse

class SubLevelProgressResponse(BaseModel):
    """Response DTO untuk progress sublevel"""
    sublevel_id: int
    sublevel_name: str
    level_name: str
    is_unlocked: bool
    status: str
    completion_percentage: int
    stars: int
    best_stars: int
    attempts: int
    best_score: int
    is_completed: bool
    last_attempt: Optional[str]
    completed_at: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "sublevel_id": 1,
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner",
                "is_unlocked": True,
                "status": "completed",
                "completion_percentage": 85,
                "stars": 2,
                "best_stars": 2,
                "attempts": 1,
                "best_score": 85,
                "is_completed": True,
                "last_attempt": "2025-10-09T10:30:00",
                "completed_at": "2025-10-09T10:30:00"
            }
        }

class AvailableSubLevelResponse(BaseModel):
    """Response DTO untuk available sublevels"""
    sublevel_id: int
    sublevel_name: str
    level_name: str
    level_id: int
    description: Optional[str]
    is_unlocked: bool
    is_completed: bool
    stars: int
    attempts: int
    best_score: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "sublevel_id": 1,
                "sublevel_name": "Alphabet A-E",
                "level_name": "Beginner",
                "level_id": 1,
                "description": "Belajar huruf A sampai E",
                "is_unlocked": True,
                "is_completed": True,
                "stars": 2,
                "attempts": 1,
                "best_score": 85
            }
        }

class UserProgressSummaryResponse(BaseModel):
    """Response untuk overall progress summary"""
    overall_summary: Dict[str, Any]
    progress_by_level: Dict[str, Any]
    unlocked_levels: List[int]
    user_id: int
    username: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_summary": {
                    "total_sublevels": 15,
                    "completed_sublevels": 5,
                    "completion_rate": 33.33,
                    "total_stars": 12
                },
                "progress_by_level": {
                    "Beginner": {
                        "level_id": 1,
                        "total_sublevels": 5,
                        "completed": 5,
                        "total_stars": 15,
                        "unlocked": 5,
                        "is_level_unlocked": True,
                        "is_level_completed": True
                    }
                },
                "unlocked_levels": [1, 2],
                "user_id": 1,
                "username": "john_doe"
            }
        }

class LevelProgressSummary(BaseModel):
    """Summary progress per level"""
    total_sublevels: int
    completed: int
    total_stars: int
    unlocked: int

class ResetProgressResponse(BaseModel):
    """Response untuk reset progress"""
    success: bool
    message: str
    sublevel_id: int

# =====================================================================
# GENERAL RESPONSE DTOs
# =====================================================================

class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    
class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None