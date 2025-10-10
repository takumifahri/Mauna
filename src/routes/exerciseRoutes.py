from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from src.database.db import get_db
from src.models.user import User
from src.config.middleware import get_current_user
from src.handler.user.kerjakanSoal import SoalHandler
from src.dto.exercise_dto import (
    FinishQuizRequest,
    StartQuizResponse,
    FinishQuizResponse,
    SubLevelProgressResponse,
    UserProgressSummaryResponse,
    AvailableSubLevelResponse,
    ResetProgressResponse,
    ApiResponse
)
router = APIRouter(prefix="/user/soal", tags=["User - Soal"])

# =====================================================================
# QUIZ ENDPOINTS
# =====================================================================

@router.get("/sublevel/{sublevel_id}/start", response_model=StartQuizResponse)
async def start_quiz(
    sublevel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🎯 Start quiz untuk sublevel tertentu"""
    try:
        handler = SoalHandler(db)
        # ✅ Use helper method instead of direct access
        quiz_data = handler.start_quiz(current_user.get_id(), sublevel_id)
        
        return StartQuizResponse(
            success=True,
            message=f"Quiz dimulai untuk {quiz_data.sublevel_name}",
            data=quiz_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat memulai quiz"
        )

@router.post("/sublevel/{sublevel_id}/finish", response_model=FinishQuizResponse)
async def finish_quiz(
    sublevel_id: int,
    quiz_data: FinishQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🏁 Finish quiz dan update progress"""
    try:
        handler = SoalHandler(db)
        # ✅ Use helper method
        result = handler.finish_quiz(current_user.get_id(), sublevel_id, quiz_data)
        
        if result.is_completed:
            message = f"🎉 Selamat! Anda berhasil menyelesaikan quiz dengan {result.stars} bintang!"
        else:
            message = f"💪 Coba lagi! Anda memerlukan minimal 60% untuk lulus. Skor Anda: {result.completion_percentage}%"
        
        return FinishQuizResponse(
            success=True,
            message=message,
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error finishing quiz: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat menyelesaikan quiz"
        )

@router.get("/sublevel/{sublevel_id}/progress", response_model=SubLevelProgressResponse)
async def get_sublevel_progress(
    sublevel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📊 Get progress untuk sublevel tertentu"""
    try:
        handler = SoalHandler(db)
        # ✅ Use helper method
        return handler.get_sublevel_progress(current_user.get_id(), sublevel_id)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat mengambil progress"
        )

@router.get("/user/progress/summary", response_model=UserProgressSummaryResponse)
async def get_user_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📈 Get overall progress summary untuk user"""
    try:
        handler = SoalHandler(db)
        # ✅ Use helper methods
        summary_data = handler.get_user_progress_summary(current_user.get_id())
        
        return UserProgressSummaryResponse(
            overall_summary=summary_data["overall_summary"],
            progress_by_level=summary_data["progress_by_level"],
            unlocked_levels=summary_data["unlocked_levels"],
            user_id=current_user.get_id(),
            username=current_user.get_username()
        )
        
    except Exception as e:
        print(f"Error getting user progress summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat mengambil ringkasan progress"
        )

@router.get("/available-sublevels", response_model=List[AvailableSubLevelResponse])
async def get_available_sublevels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """📋 Get all available sublevels dengan status unlock"""
    try:
        handler = SoalHandler(db)
        # ✅ Use helper method
        return handler.get_available_sublevels(current_user.get_id())
        
    except Exception as e:
        print(f"Error getting available sublevels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat mengambil daftar sublevel"
        )

@router.post("/sublevel/{sublevel_id}/reset", response_model=ResetProgressResponse)
async def reset_sublevel_progress(
    sublevel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """🔄 Reset progress untuk sublevel"""
    try:
        handler = SoalHandler(db)
        # ✅ Use helper method
        reset_sublevel_id = handler.reset_sublevel_progress(current_user.get_id(), sublevel_id)
        
        return ResetProgressResponse(
            success=True,
            message="Progress berhasil direset",
            sublevel_id=reset_sublevel_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resetting progress: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat mereset progress"
        )

@router.get("/health", response_model=ApiResponse)
async def health_check():
    """❤️ Health check endpoint"""
    return ApiResponse(
        success=True,
        message="Soal service is running properly",
        data={"status": "healthy", "service": "soal"}
    )

# =====================================================================
# 🔥 NEW: STREAK ENDPOINTS
# =====================================================================

@router.get("/streak/info", response_model=Dict[str, Any])
async def get_user_streak_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔥 Get user's current streak information
    
    Returns:
    - current_streak: Jumlah hari berturut-turut
    - longest_streak: Rekor streak terpanjang
    - tier: Tier saat ini (bronze/silver/gold/diamond/platinum)
    - streak_freeze_count: Jumlah freeze yang tersisa
    - days_to_next_tier: Hari lagi untuk tier berikutnya
    """
    try:
        handler = SoalHandler(db)
        result = handler.get_user_streak_info(current_user.get_id())
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to get streak info")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting streak info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat mengambil informasi streak"
        )

@router.post("/streak/freeze", response_model=ApiResponse)
async def use_streak_freeze(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🧊 Use streak freeze to protect streak
    
    Gunakan 1 streak freeze untuk protect streak saat tidak bisa belajar
    """
    try:
        user = db.query(User).filter(User.id == current_user.get_id()).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.use_streak_freeze():
            db.commit()
            return ApiResponse(
                success=True,
                message=f"Streak freeze activated! Remaining: {user.streak_freeze_count}",
                data={
                    "streak_freeze_remaining": user.streak_freeze_count
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No streak freeze available"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error using streak freeze: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat menggunakan streak freeze"
        )