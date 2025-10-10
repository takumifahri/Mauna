from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from datetime import datetime
from ..database.db import Base

class ProgressStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Progress(Base):
    __tablename__ = "progress"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sublevel_id = Column(Integer, ForeignKey("sublevel.id", ondelete="CASCADE"), nullable=False)
    
    # Progress Status
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False)
    
    # Score & Completion Fields
    total_questions = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    stars = Column(Integer, default=0, nullable=False)  # Current stars (0-3)
    completion_percentage = Column(Integer, default=0, nullable=False)
    
    # Best Performance Tracking
    attempts = Column(Integer, default=0, nullable=False)
    best_score = Column(Integer, default=0, nullable=False)
    best_stars = Column(Integer, default=0, nullable=False)
    
    # Unlock System
    is_unlocked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    last_attempt = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user_ref = relationship("User", back_populates="progress_list")
    sublevel_ref = relationship("SubLevel", back_populates="progress_list")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'sublevel_id', name='uq_user_sublevel_progress'),
    )
    
    def __repr__(self):
        return (f"<Progress(id={self.id}, user_id={self.user_id}, "
                f"sublevel_id={self.sublevel_id}, status={self.status.value}, "
                f"stars={self.stars}, score={self.score})>")
    
    # =====================================================================
    # HELPER METHODS
    # =====================================================================
    
    def calculate_stars(self, percentage: float) -> int:
        """
        Calculate stars based on completion percentage
        
        Args:
            percentage: Completion percentage (0-100)
            
        Returns:
            int: Number of stars (0-3)
        """
        if percentage >= 95:
            return 3  # ⭐⭐⭐ Perfect
        elif percentage >= 80:
            return 2  # ⭐⭐ Great
        elif percentage >= 60:
            return 1  # ⭐ Good
        else:
            return 0  # No stars
    
    def update_completion(self, correct: int, total: int, score: int):
        """
        Update progress after completing sublevel
        
        Args:
            correct: Number of correct answers
            total: Total number of questions
            score: Score achieved
        """
        # Update current attempt data
        self.correct_answers = correct
        self.total_questions = total
        self.score = score
        self.completion_percentage = int((correct / total) * 100) if total > 0 else 0
        
        # Calculate stars for current attempt
        current_stars = self.calculate_stars(self.completion_percentage)
        self.stars = current_stars
        
        # Increment attempt counter
        self.attempts = (self.attempts or 0) + 1
        
        # Update best performance tracking
        current_best_score = self.best_score or 0
        current_best_stars = self.best_stars or 0
        
        if score > current_best_score: # type: ignore
            self.best_score = score
            
        if current_stars > current_best_stars: # type: ignore
            self.best_stars = current_stars
        
        # Update status based on performance
        if self.completion_percentage >= 60:
            self.status = ProgressStatus.COMPLETED
            self.completed_at = datetime.now()
        else:
            self.status = ProgressStatus.FAILED
        
        # Update last attempt timestamp
        self.last_attempt = datetime.now()
    
    def start_progress(self):
        """Mark progress as started"""
        if self.status is ProgressStatus.NOT_STARTED:
            self.status = ProgressStatus.IN_PROGRESS
    
    def reset_progress(self):
        """Reset progress to initial state (keep best scores)"""
        self.status = ProgressStatus.NOT_STARTED
        self.correct_answers = 0
        self.score = 0
        self.stars = 0
        self.completion_percentage = 0
        # Note: Keep attempts, best_score, best_stars for history
    
    def unlock(self):
        """Unlock this sublevel for the user"""
        self.is_unlocked = True
    
    # =====================================================================
    # PROPERTIES
    # =====================================================================
    
    @hybrid_property
    def is_completed(self) -> bool:
        """Check if sublevel is completed (passed)"""
        return self.status is ProgressStatus.COMPLETED
    
    @hybrid_property
    def is_failed(self) -> bool:
        """Check if sublevel failed on last attempt"""
        return self.status is ProgressStatus.FAILED
    
    @hybrid_property
    def is_in_progress(self) -> bool:
        """Check if sublevel is currently in progress"""
        return self.status is ProgressStatus.IN_PROGRESS
    
    @hybrid_property
    def has_attempts(self):
        """Check if user has attempted this sublevel"""
        return (self.attempts or 0) > 0
    
    @hybrid_property
    def success_rate(self):
        """Calculate success rate as percentage"""
<<<<<<< HEAD
        if self.total_questions == 0:
=======
        if self.total_questions == 0:  # type: ignore
>>>>>>> 03f67aacdd09a30595b9d5c2b592966cc5ef3fe8
            return 0.0
        return (self.correct_answers / self.total_questions) * 100
    
    @hybrid_property
    def is_perfect_score(self) -> bool:
        """Check if user got perfect score (100%)"""
<<<<<<< HEAD
        return self.completion_percentage == 100
=======
        return self.completion_percentage == 100  # type: ignore
>>>>>>> 03f67aacdd09a30595b9d5c2b592966cc5ef3fe8
    
    # =====================================================================
    # CLASS METHODS
    # =====================================================================
    
    @classmethod
    def get_or_create(cls, db_session, user_id: int, sublevel_id: int):
        """
        Get existing progress or create new one
        
        Args:
            db_session: SQLAlchemy session
            user_id: User ID
            sublevel_id: SubLevel ID
            
        Returns:
            Progress: Existing or new progress instance
        """
        progress = db_session.query(cls).filter_by(
            user_id=user_id,
            sublevel_id=sublevel_id
        ).first()
        
        if not progress:
            progress = cls(
                user_id=user_id,
                sublevel_id=sublevel_id,
                status=ProgressStatus.NOT_STARTED,
                is_unlocked=False
            )
            db_session.add(progress)
            db_session.flush()  # Get ID without committing
        
        return progress
    
    @classmethod
    def get_user_progress_summary(cls, db_session, user_id: int):
        """
        Get overall progress summary for user
        
        Args:
            db_session: SQLAlchemy session
            user_id: User ID
            
        Returns:
            dict: Progress summary statistics
        """
        progress_list = db_session.query(cls).filter_by(user_id=user_id).all()
        
        total_sublevels = len(progress_list)
        completed = len([p for p in progress_list if p.is_completed])
        total_stars = sum(p.best_stars for p in progress_list)
        total_attempts = sum(p.attempts for p in progress_list)
        
        return {
            "total_sublevels": total_sublevels,
            "completed_sublevels": completed,
            "completion_rate": (completed / total_sublevels * 100) if total_sublevels > 0 else 0,
            "total_stars": total_stars,
            "total_attempts": total_attempts,
            "average_score": sum(p.best_score for p in progress_list) / total_sublevels if total_sublevels > 0 else 0
        }