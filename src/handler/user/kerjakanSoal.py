from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from datetime import date, datetime

from src.models.user import User
from src.models.sublevel import SubLevel
from src.models.level import Level
from src.models.soal import Soal
from src.models.progress import Progress, ProgressStatus
from src.dto.exercise_dto import (
    SoalResponse, QuizDataResponse, QuizResultResponse,
    SubLevelProgressResponse, AvailableSubLevelResponse,
    FinishQuizRequest
)
import random
import json

class SoalHandler:
    """Handler untuk business logic terkait soal dan quiz"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================================
    # TYPE-SAFE HELPER METHODS - Convert SQLAlchemy objects to Python types
    # =====================================================================
    
    @staticmethod
    def get_int(value: Any) -> int:
        """Safely convert to int"""
        return int(value) if value is not None else 0
    
    @staticmethod
    def get_str(value: Any) -> str:
        """Safely convert to str"""
        return str(value) if value is not None else ""
    
    @staticmethod
    def get_bool(value: Any) -> bool:
        """Safely convert to bool"""
        return bool(value) if value is not None else False
    
    @staticmethod
    def get_optional_str(value: Any) -> Optional[str]:
        """Safely convert to optional str"""
        return str(value) if value is not None else None
    
    # =====================================================================
    # LEVEL UNLOCK SYSTEM - Progressive unlock based on level completion
    # =====================================================================
    
    def is_level_completed(self, user_id: int, level_id: int) -> bool:
        """
        Check if ALL sublevels in a level are completed
        
        Returns:
            bool: True jika semua sublevel di level ini sudah completed
        """
        # Get all sublevels in this level
        sublevels = self.db.query(SubLevel).filter(
            SubLevel.level_id == level_id,
            SubLevel.deleted_at.is_(None)
        ).all()
        
        if not sublevels:
            return False
        
        # Check if all sublevels are completed
        for sublevel in sublevels:
            progress = self.db.query(Progress).filter(
                Progress.user_id == user_id,
                Progress.sublevel_id == sublevel.id
            ).first()
            
            # If any sublevel is not completed, return False
            if not progress or not self.get_bool(progress.is_completed):
                return False
        
        return True
    
    def get_unlocked_levels(self, user_id: int) -> List[int]:
        """
        Get list of level IDs yang sudah unlocked untuk user
        
        Logic:
        1. Level 1 always unlocked
        2. Level N unlocked jika level N-1 fully completed
        
        Returns:
            List[int]: List of unlocked level IDs
        """
        # Get all levels ordered by ID
        all_levels = self.db.query(Level).filter(
            Level.deleted_at.is_(None)
        ).order_by(Level.id).all()
        
        if not all_levels:
            return []
        
        unlocked_levels = []
        
        for idx, level in enumerate(all_levels):
            level_id = self.get_int(level.id)
            
            if idx == 0:
                # Level pertama selalu unlocked
                unlocked_levels.append(level_id)
            else:
                # Level selanjutnya unlocked jika level sebelumnya completed
                prev_level_id = self.get_int(all_levels[idx - 1].id)
                if self.is_level_completed(user_id, prev_level_id):
                    unlocked_levels.append(level_id)
                else:
                    # Jika level sebelumnya belum completed, stop checking
                    break
        
        return unlocked_levels
    
    def unlock_level_sublevels(self, user_id: int, level_id: int):
        """
        Unlock FIRST sublevel di level yang baru terbuka
        
        Args:
            user_id: User ID
            level_id: Level ID yang baru unlocked
        """
        # Get first sublevel in this level
        first_sublevel = self.db.query(SubLevel).filter(
            SubLevel.level_id == level_id,
            SubLevel.deleted_at.is_(None)
        ).order_by(SubLevel.id).first()
        
        if first_sublevel:
            progress = Progress.get_or_create(
                self.db, 
                user_id, 
                self.get_int(first_sublevel.id)
            )
            if not self.get_bool(progress.is_unlocked):
                progress.unlock()
                self.db.commit()
    
    def is_sublevel_accessible(self, user_id: int, sublevel_id: int) -> tuple[bool, str]:
        """
        Check if sublevel is accessible untuk user
        
        Returns:
            tuple[bool, str]: (is_accessible, error_message)
        """
        sublevel = self.db.query(SubLevel).filter(
            SubLevel.id == sublevel_id,
            SubLevel.deleted_at.is_(None)
        ).first()
        
        if not sublevel:
            return False, "SubLevel tidak ditemukan"
        
        level_id = self.get_int(sublevel.level_id)
        
        # Check if level is unlocked
        unlocked_levels = self.get_unlocked_levels(user_id)
        if level_id not in unlocked_levels:
            return False, "Level ini belum terbuka. Selesaikan semua sublevel di level sebelumnya terlebih dahulu."
        
        # Check if sublevel is unlocked
        progress = Progress.get_or_create(self.db, user_id, sublevel_id)
        if not self.get_bool(progress.is_unlocked):
            return False, "SubLevel ini belum terbuka. Selesaikan sublevel sebelumnya terlebih dahulu."
        
        return True, ""
    
    # =====================================================================
    # BUSINESS LOGIC HELPER METHODS
    # =====================================================================
    
    def get_sublevel_questions(self, sublevel_id: int) -> List[Soal]:
        """Get all questions for a sublevel with related data"""
        return self.db.query(Soal).options(
            joinedload(Soal.kamus_ref),
            joinedload(Soal.sublevel_ref).joinedload(SubLevel.level_ref)
        ).filter(
            Soal.sublevel_id == sublevel_id,
            Soal.deleted_at.is_(None)
        ).all()
    
    def create_soal_response(self, soal: Soal) -> SoalResponse:
        """Convert Soal model to SoalResponse - Duolingo style with full data"""
        return SoalResponse(
            id=self.get_int(soal.id),
            question=self.get_str(soal.question),
            video_url=self.get_optional_str(soal.video_url),
            image_url=self.get_optional_str(soal.image_url),
            dictionary_word=self.get_str(soal.kamus_ref.word_text) if soal.kamus_ref else None,
            dictionary_definition=self.get_str(soal.kamus_ref.definition) if soal.kamus_ref else None,
            dictionary_video_url=self.get_optional_str(soal.kamus_ref.video_url) if soal.kamus_ref else None,
            dictionary_image_url=self.get_optional_str(soal.kamus_ref.image_url_ref) if soal.kamus_ref else None,
            sublevel_name=self.get_str(soal.sublevel_ref.name),
            level_name=self.get_str(soal.sublevel_ref.level_ref.name)
        )
    
    def unlock_next_sublevel(self, user_id: int, current_sublevel_id: int) -> bool:
        """
        Unlock next sublevel atau level jika current sublevel completed
        
        Returns:
            bool: True jika ada yang di-unlock
        """
        try:
            current_sublevel = self.db.query(SubLevel).filter(
                SubLevel.id == current_sublevel_id
            ).first()
            
            if not current_sublevel:
                return False
            
            current_level_id = self.get_int(current_sublevel.level_id)
            
            # Get next sublevel in the same level
            next_sublevel = self.db.query(SubLevel).filter(
                SubLevel.level_id == current_level_id,
                SubLevel.id > current_sublevel_id,
                SubLevel.deleted_at.is_(None)
            ).order_by(SubLevel.id).first()
            
            if next_sublevel:
                # Unlock next sublevel dalam level yang sama
                next_progress = Progress.get_or_create(
                    self.db, 
                    user_id, 
                    self.get_int(next_sublevel.id)
                )
                if not self.get_bool(next_progress.is_unlocked):
                    next_progress.unlock()
                    self.db.commit()
                    return True
            else:
                # No more sublevels in current level
                # Check if level is fully completed
                if self.is_level_completed(user_id, current_level_id):
                    # Find next level
                    next_level = self.db.query(Level).filter(
                        Level.id > current_level_id,
                        Level.deleted_at.is_(None)
                    ).order_by(Level.id).first()
                    
                    if next_level:
                        # Unlock first sublevel of next level
                        next_level_id = self.get_int(next_level.id)
                        self.unlock_level_sublevels(user_id, next_level_id)
                        return True
            
            return False
        except Exception as e:
            print(f"Error unlocking next sublevel: {e}")
            return False
    
    def initialize_user_progress(self, user_id: int):
        """
        Initialize progress untuk user baru
        - Unlock level 1
        - Unlock sublevel pertama di level 1
        """
        # Get first level
        first_level = self.db.query(Level).filter(
            Level.deleted_at.is_(None)
        ).order_by(Level.id).first()
        
        if first_level:
            level_id = self.get_int(first_level.id)
            self.unlock_level_sublevels(user_id, level_id)
    
    # =====================================================================
    # MAIN BUSINESS LOGIC METHODS
    # =====================================================================
    
    def start_quiz(self, user_id: int, sublevel_id: int) -> QuizDataResponse:
        """Start quiz untuk sublevel tertentu - 10 soal acak per user per sublevel"""
        # Check if sublevel exists
        sublevel = self.db.query(SubLevel).options(
            joinedload(SubLevel.level_ref)
        ).filter(
            SubLevel.id == sublevel_id,
            SubLevel.deleted_at.is_(None)
        ).first()
        
        if not sublevel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SubLevel tidak ditemukan"
            )
        
        # ✅ Check accessibility (level & sublevel unlock)
        is_accessible, error_msg = self.is_sublevel_accessible(user_id, sublevel_id)
        if not is_accessible:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg
            )
        
        # Get or create progress
        progress = Progress.get_or_create(self.db, user_id, sublevel_id)

        # --- NEW: Randomize 10 soal per user per sublevel ---
        # Simpan soal terpilih di progress (misal field: selected_soal_ids, type: TEXT/JSON)
        selected_soal_ids = None
        if hasattr(progress, "selected_soal_ids") and progress.selected_soal_ids:
            try:
                selected_soal_ids = json.loads(progress.selected_soal_ids)
            except Exception:
                selected_soal_ids = None

        if not selected_soal_ids:
            # Ambil semua soal di sublevel
            all_soal = self.db.query(Soal).filter(
                Soal.sublevel_id == sublevel_id,
                Soal.deleted_at.is_(None)
            ).all()
            if len(all_soal) < 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Jumlah soal di sublevel ini kurang dari 10"
                )
            # Random 10 soal unik
            selected_soal = random.sample(all_soal, 10)
            selected_soal_ids = [soal.id for soal in selected_soal]
            # Simpan ke progress
            progress.selected_soal_ids = json.dumps(selected_soal_ids)
            self.db.commit()
        else:
            # Ambil soal sesuai ID yang sudah dipilih
            selected_soal = self.db.query(Soal).filter(
                Soal.id.in_(selected_soal_ids),
                Soal.deleted_at.is_(None)
            ).all()

        if not selected_soal or len(selected_soal) < 10:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tidak ada soal ditemukan untuk sublevel ini"
            )
        
        # Convert to response format
        question_responses = [self.create_soal_response(soal) for soal in selected_soal]
        
        # Mark progress as started
        progress.start_progress()
        self.db.commit()
        
        return QuizDataResponse(
            sublevel_id=self.get_int(sublevel.id),
            sublevel_name=self.get_str(sublevel.name),
            sublevel_description=self.get_optional_str(sublevel.description),
            level_name=self.get_str(sublevel.level_ref.name),
            total_questions=len(question_responses),
            questions=question_responses,
            progress_status=self.get_str(progress.status.value),
            is_unlocked=self.get_bool(progress.is_unlocked),
            current_attempt=self.get_int(progress.attempts) + 1,
            best_score=self.get_int(progress.best_score),
            best_stars=self.get_int(progress.best_stars)
        )
    

  
    # =====================================================================
    # 🔥 NEW: DAILY STREAK TRACKING
    # =====================================================================
    
    def update_user_streak(self, user_id: int, activity_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Update user streak saat menyelesaikan quiz
        
        Args:
            user_id: User ID
            activity_date: Tanggal aktivitas (default: today)
        
        Returns:
            Dict dengan info streak update
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": "User not found",
                    "streak_updated": False
                }
            
            # Set activity date
            if activity_date is None:
                activity_date = date.today()
            
            # Get previous streak values
            prev_streak = self.get_int(user.current_streak)
            prev_longest = self.get_int(user.longest_streak)
            prev_tier = user.tier.value if user.tier is not None else "bronze"
            
            # ✅ Update streak using User model method
            user.update_streak(activity_date)
            
            # Commit changes
            self.db.commit()
            self.db.refresh(user)
            
            # Get new values
            new_streak = self.get_int(user.current_streak)
            new_longest = self.get_int(user.longest_streak)
            new_tier = user.tier.value if user.tier is not None else "bronze"
            
            # Check if streak increased
            streak_increased = new_streak > prev_streak
            tier_upgraded = new_tier != prev_tier and new_tier != prev_tier
            
            return {
                "success": True,
                "streak_updated": True,
                "previous_streak": prev_streak,
                "current_streak": new_streak,
                "longest_streak": new_longest,
                "streak_increased": streak_increased,
                "tier": new_tier,
                "tier_upgraded": tier_upgraded,
                "last_activity_date": user.last_activity_date.isoformat() if user.last_activity_date is not None else None
            }
            
        except Exception as e:
            print(f"❌ Error updating user streak: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to update streak: {str(e)}",
                "streak_updated": False
            }
    
    def get_user_streak_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get user streak information
        
        Returns:
            Dict dengan informasi streak lengkap
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            current_streak = self.get_int(user.current_streak)
            longest_streak = self.get_int(user.longest_streak)
            tier = user.tier.value if user.tier is not None else "bronze"
            
            # Get next tier threshold
            next_threshold = user.get_next_tier_threshold()
            days_to_next_tier = None
            if next_threshold:
                days_to_next_tier = next_threshold - current_streak
            
            return {
                "success": True,
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "tier": tier,
                "tier_display": tier.capitalize(),
                "last_activity_date": user.last_activity_date.isoformat() if user.last_activity_date is not None else None,
                "streak_freeze_count": self.get_int(user.streak_freeze_count),
                "next_tier_threshold": next_threshold,
                "days_to_next_tier": days_to_next_tier,
                "total_quizzes_completed": self.get_int(user.total_quizzes_completed),
                "total_xp": self.get_int(user.total_xp)
            }
            
        except Exception as e:
            print(f"❌ Error getting user streak info: {e}")
            return {
                "success": False,
                "message": f"Failed to get streak info: {str(e)}"
            }
    
    # =====================================================================
    # 🔥 UPDATED: finish_quiz WITH STREAK TRACKING
    # =====================================================================
    
    def finish_quiz(self, user_id: int, sublevel_id: int, quiz_data: FinishQuizRequest) -> QuizResultResponse:
        """
        Finish quiz dan update progress + daily streak
        
        ✅ NEW: Automatically updates daily streak saat quiz completed
        """
        
        if quiz_data.sublevel_id != sublevel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SubLevel ID tidak konsisten"
            )
        
        sublevel = self.db.query(SubLevel).filter(
            SubLevel.id == sublevel_id,
            SubLevel.deleted_at.is_(None)
        ).first()
        
        if not sublevel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SubLevel tidak ditemukan"
            )
        
        progress = Progress.get_or_create(self.db, user_id, sublevel_id)
        
        # Get total questions for validation
        total_questions_db = self.db.query(Soal).filter(
            Soal.sublevel_id == sublevel_id,
            Soal.deleted_at.is_(None)
        ).count()
        
        # Validate jumlah correct answers
        if quiz_data.correct_answers > total_questions_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Jumlah jawaban benar tidak valid. Max: {total_questions_db}, Got: {quiz_data.correct_answers}"
            )
        
        # Validate score range
        if quiz_data.total_score < 0 or quiz_data.total_score > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total score harus antara 0-100"
            )
        
        # Update progress
        # Update progress
        progress.update_completion(
            correct=quiz_data.correct_answers,
            total=total_questions_db,
            score=quiz_data.total_score
        )
        # Tambah XP ke user
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Misal: 1 XP per soal yang dijawab, atau sesuai score
            xp_gained = quiz_data.correct_answers  # atau quiz_data.total_score // 10
            user.add_xp(xp_gained)
            user.increment_quiz_count()
        
        # ✅ NEW: Update daily streak saat quiz completed
        streak_info = self.update_user_streak(user_id)
        
        # ✅ Increment quiz count
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.increment_quiz_count()
        
        # Unlock next sublevel or level if completed
        next_sublevel_unlocked = False
        if self.get_bool(progress.is_completed):
            next_sublevel_unlocked = self.unlock_next_sublevel(user_id, sublevel_id)
        
        self.db.commit()
        
        # Return response dengan streak info
        result = QuizResultResponse(
            score=self.get_int(progress.score),
            correct_answers=self.get_int(progress.correct_answers),
            total_questions=self.get_int(progress.total_questions),
            completion_percentage=self.get_int(progress.completion_percentage),
            stars=self.get_int(progress.stars),
            status=self.get_str(progress.status.value),
            attempts=self.get_int(progress.attempts),
            best_score=self.get_int(progress.best_score),
            best_stars=self.get_int(progress.best_stars),
            is_completed=self.get_bool(progress.is_completed),
            next_sublevel_unlocked=next_sublevel_unlocked
        )
        
        # ✅ Add streak info to response metadata (optional)
        print(f"✅ Quiz completed! Streak info: {streak_info}")
        
        return result
    
    def get_sublevel_progress(self, user_id: int, sublevel_id: int) -> SubLevelProgressResponse:
        """Get progress untuk sublevel tertentu"""
        
        sublevel = self.db.query(SubLevel).options(
            joinedload(SubLevel.level_ref)
        ).filter(
            SubLevel.id == sublevel_id,
            SubLevel.deleted_at.is_(None)
        ).first()
        
        if not sublevel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SubLevel tidak ditemukan"
            )
        
        progress = Progress.get_or_create(self.db, user_id, sublevel_id)
        
        last_attempt_str = progress.last_attempt.isoformat() if progress.last_attempt is not None else None
        completed_at_str = progress.completed_at.isoformat() if progress.completed_at is not None else None
        
        return SubLevelProgressResponse(
            sublevel_id=self.get_int(sublevel.id),
            sublevel_name=self.get_str(sublevel.name),
            level_name=self.get_str(sublevel.level_ref.name),
            is_unlocked=self.get_bool(progress.is_unlocked),
            status=self.get_str(progress.status.value),
            completion_percentage=self.get_int(progress.completion_percentage),
            stars=self.get_int(progress.stars),
            best_stars=self.get_int(progress.best_stars),
            attempts=self.get_int(progress.attempts),
            best_score=self.get_int(progress.best_score),
            is_completed=self.get_bool(progress.is_completed),
            last_attempt=last_attempt_str,
            completed_at=completed_at_str
        )
    
    def get_user_progress_summary(self, user_id: int) -> Dict[str, Any]:
        """Get overall progress summary dengan level unlock info"""
        
        # Initialize progress jika belum ada
        self.initialize_user_progress(user_id)
        
        summary = Progress.get_user_progress_summary(self.db, user_id)
        
        # Get unlocked levels
        unlocked_levels = self.get_unlocked_levels(user_id)
        
        # Get detailed progress by level
        all_levels = self.db.query(Level).filter(
            Level.deleted_at.is_(None)
        ).order_by(Level.id).all()
        
        level_progress: Dict[str, Dict[str, Any]] = {}
        
        for level in all_levels:
            level_id = self.get_int(level.id)
            level_name = self.get_str(level.name)
            
            # Get all sublevels in this level
            sublevels = self.db.query(SubLevel).filter(
                SubLevel.level_id == level_id,
                SubLevel.deleted_at.is_(None)
            ).all()
            
            total_sublevels = len(sublevels)
            completed = 0
            total_stars = 0
            unlocked = 0
            
            for sublevel in sublevels:
                progress = self.db.query(Progress).filter(
                    Progress.user_id == user_id,
                    Progress.sublevel_id == sublevel.id
                ).first()
                
                if progress:
                    if self.get_bool(progress.is_completed):
                        completed += 1
                    if self.get_bool(progress.is_unlocked):
                        unlocked += 1
                    total_stars += self.get_int(progress.best_stars)
            
            level_progress[level_name] = {
                "level_id": level_id,
                "total_sublevels": total_sublevels,
                "completed": completed,
                "total_stars": total_stars,
                "unlocked": unlocked,
                "is_level_unlocked": level_id in unlocked_levels,
                "is_level_completed": self.is_level_completed(user_id, level_id)
            }
        
        return {
            "overall_summary": summary,
            "progress_by_level": level_progress,
            "unlocked_levels": unlocked_levels
        }
    
    def get_available_sublevels(self, user_id: int) -> List[AvailableSubLevelResponse]:
        """Get all sublevels dengan status unlock berdasarkan level completion"""
        
        # Initialize progress untuk user baru
        self.initialize_user_progress(user_id)
        
        # Get unlocked levels
        unlocked_levels = self.get_unlocked_levels(user_id)
        
        # Get all sublevels
        sublevels = self.db.query(SubLevel).options(
            joinedload(SubLevel.level_ref)
        ).filter(
            SubLevel.deleted_at.is_(None)
        ).order_by(SubLevel.level_id, SubLevel.id).all()
        
        result = []
        for sublevel in sublevels:
            level_id = self.get_int(sublevel.level_id)
            sublevel_id = self.get_int(sublevel.id)
            
            # Check if level is unlocked
            is_level_unlocked = level_id in unlocked_levels
            
            progress = Progress.get_or_create(self.db, user_id, sublevel_id)
            
            # Auto-unlock first sublevel in unlocked levels
            if is_level_unlocked and not self.get_bool(progress.is_unlocked):
                # Check if this is first sublevel in level
                first_sublevel = self.db.query(SubLevel).filter(
                    SubLevel.level_id == level_id,
                    SubLevel.deleted_at.is_(None)
                ).order_by(SubLevel.id).first()
                
                if first_sublevel and sublevel_id == self.get_int(first_sublevel.id):
                    progress.unlock()
            
            description_str = self.get_optional_str(sublevel.description)
            
            result.append(AvailableSubLevelResponse(
                sublevel_id=sublevel_id,
                sublevel_name=self.get_str(sublevel.name),
                level_name=self.get_str(sublevel.level_ref.name),
                level_id=level_id,
                description=description_str,
                is_unlocked=self.get_bool(progress.is_unlocked),
                is_completed=self.get_bool(progress.is_completed),
                stars=self.get_int(progress.best_stars),
                attempts=self.get_int(progress.attempts),
                best_score=self.get_int(progress.best_score)
            ))
        
        self.db.commit()
        return result
    
    def reset_sublevel_progress(self, user_id: int, sublevel_id: int) -> int:
        """Reset progress untuk sublevel"""
        
        progress = self.db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.sublevel_id == sublevel_id
        ).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress tidak ditemukan"
            )
        
        progress.reset_progress()
        self.db.commit()
        
        return sublevel_id