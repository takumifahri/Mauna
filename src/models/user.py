from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, event, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
import enum
from .user_badge import user_badge_association
from ..database.db import Base

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class UserTier(enum.Enum):
    """User tier based on streak"""
    BRONZE = "bronze"      # 1-6 days streak
    SILVER = "silver"      # 7-29 days streak
    GOLD = "gold"          # 30-89 days streak
    DIAMOND = "diamond"    # 90-179 days streak
    PLATINUM = "platinum"  # 180+ days streak

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(50), unique=True, index=True, nullable=False)
    username = Column(String(255), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    nama = Column(String(255), nullable=True)
    telpon = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    total_badges = Column(Integer, default=0)
    avatar_url = Column(String(255), nullable=True)
    # STREAK TRACKING FIELDS
    current_streak = Column(Integer, default=0, nullable=True)
    longest_streak = Column(Integer, default=0, nullable=True)
    last_activity_date = Column(Date, nullable=True)
    streak_freeze_count = Column(Integer, default=0, nullable=True)
    
    # TIER SYSTEM
    tier = Column(Enum(UserTier), default=UserTier.BRONZE, nullable=True)
    
    # GAMIFICATION STATS
    total_xp = Column(Integer, default=0, nullable=True)
    total_quizzes_completed = Column(Integer, default=0, nullable=True)
    
    # Relasi many-to-many dengan Badge
    badges = relationship(
        "Badge",
        secondary=user_badge_association,
        back_populates="users",
        lazy="dynamic",
        cascade="save-update, merge"
    )
    
    # Relasi dengan Progress
    progress_list = relationship(
        "Progress",
        back_populates="user_ref",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # =====================================================================
    # HELPER METHODS - Type-safe accessors
    # =====================================================================
    
    def get_id(self) -> int:
        """Get user ID as Python int"""
        return int(self.id) if self.id is not None else 0  # type: ignore
    
    def get_username(self) -> str:
        """Get username as Python str"""
        return str(self.username) if self.username is not None else ""
    
    def get_email(self) -> str:
        """Get email as Python str"""
        return str(self.email) if self.email is not None else ""
    
    def get_full_name(self) -> str:
        """Get user's full name or fallback to username"""
        if self.nama is not None and str(self.nama).strip():
            return str(self.nama)
        return str(self.username) if self.username is not None else ""
    
    def get_role_value(self) -> str:
        """Get role as string value"""
        if self.role is not None:
            return self.role.value if hasattr(self.role, 'value') else "user"
        return "user"
    
    # =====================================================================
    # TIER & STREAK METHODS
    # =====================================================================
    
    def get_tier_name(self) -> str:
        """Get tier name as string"""
        if self.tier is not None:
            return self.tier.value if hasattr(self.tier, 'value') else "bronze"
        return "bronze"
    
    def get_tier_color(self) -> str:
        """Get color code for current tier"""
        tier_colors = {
            "bronze": "#CD7F32",
            "silver": "#C0C0C0",
            "gold": "#FFD700",
            "diamond": "#B9F2FF",
            "platinum": "#E5E4E2"
        }
        return tier_colors.get(self.get_tier_name(), "#CD7F32")
    
    def get_next_tier_threshold(self) -> Optional[int]:
        """Get streak days needed for next tier"""
        thresholds = {
            "bronze": 7,
            "silver": 30,
            "gold": 90,
            "diamond": 180,
            "platinum": None
        }
        return thresholds.get(self.get_tier_name(), 7)
    
    def update_tier_based_on_streak(self) -> None:
        """Update user tier based on current streak"""
        current_streak_val = 0
        if self.current_streak is not None:
            current_streak_val = int(self.current_streak)  # type: ignore
        
        if current_streak_val >= 180:
            self.tier = UserTier.PLATINUM
        elif current_streak_val >= 90:
            self.tier = UserTier.DIAMOND
        elif current_streak_val >= 30:
            self.tier = UserTier.GOLD
        elif current_streak_val >= 7:
            self.tier = UserTier.SILVER
        else:
            self.tier = UserTier.BRONZE
    
    def update_streak(self, activity_date: Optional[date] = None) -> None:
        """
        Update user streak based on activity
        
        Args:
            activity_date: Date of activity (default: today)
        
        Logic:
        - Same day: No change
        - Next day (consecutive): Increment streak
        - Gap > 1 day: Reset streak (unless has freeze)
        """
        if activity_date is None:
            activity_date = date.today()
        
        # Initialize streak values if None - use getattr for type safety
        current = getattr(self, 'current_streak', None)
        if current is None:
            self.current_streak = 0
        
        longest = getattr(self, 'longest_streak', None)
        if longest is None:
            self.longest_streak = 0
        
        freeze = getattr(self, 'streak_freeze_count', None)
        if freeze is None:
            self.streak_freeze_count = 0
        
        last_activity = getattr(self, 'last_activity_date', None)
        
        if last_activity is None:
            # First activity ever
            self.current_streak = 1
            self.last_activity_date = activity_date
        else:
            days_diff = (activity_date - last_activity).days
            
            if days_diff == 0:
                # Same day, no change to streak
                pass
            elif days_diff == 1:
                # Consecutive day, increment streak
                current_val = int(getattr(self, 'current_streak', 0))  # type: ignore
                self.current_streak = current_val + 1
                self.last_activity_date = activity_date
            elif days_diff > 1:
                # Streak broken (unless has freeze)
                freeze_val = int(getattr(self, 'streak_freeze_count', 0))  # type: ignore
                if freeze_val > 0:
                    # Use streak freeze
                    self.streak_freeze_count = freeze_val - 1
                    self.last_activity_date = activity_date
                else:
                    # Reset streak
                    self.current_streak = 1
                    self.last_activity_date = activity_date
        
        # Update longest streak if current is higher
        current_val = int(getattr(self, 'current_streak', 0))  # type: ignore
        longest_val = int(getattr(self, 'longest_streak', 0))  # type: ignore
        if current_val > longest_val:
            self.longest_streak = current_val
        
        # Update tier based on new streak
        self.update_tier_based_on_streak()
    
    def add_xp(self, xp: int) -> None:
        """Add XP to user"""
        total = getattr(self, 'total_xp', None)
        if total is None:
            self.total_xp = xp
        else:
            self.total_xp = int(total) + xp  # type: ignore
    
    def add_streak_freeze(self, count: int = 1) -> None:
        """Add streak freeze items"""
        freeze = getattr(self, 'streak_freeze_count', None)
        if freeze is None:
            self.streak_freeze_count = count
        else:
            self.streak_freeze_count = int(freeze) + count  # type: ignore
    
    def use_streak_freeze(self) -> bool:
        """Use one streak freeze item"""
        freeze = getattr(self, 'streak_freeze_count', None)
        if freeze is None:
            self.streak_freeze_count = 0
            return False
        
        freeze_val = int(freeze)  # type: ignore
        if freeze_val > 0:
            self.streak_freeze_count = freeze_val - 1
            return True
        return False
    
    def increment_quiz_count(self) -> None:
        """Increment total quizzes completed"""
        total = getattr(self, 'total_quizzes_completed', None)
        if total is None:
            self.total_quizzes_completed = 1
        else:
            self.total_quizzes_completed = int(total) + 1  # type: ignore
    
    # =====================================================================
    # EXISTING PROPERTIES & METHODS
    # =====================================================================
    
    @hybrid_property
    def generated_unique_id(self):
        if self.id is not None:
            return f"USR-{int(self.id):05d}"  # type: ignore
        return "USR-00000"
    
    @property
    def is_admin(self) -> bool:
        if self.role is None:
            return False
        return self.role is UserRole.ADMIN
    
    @property
    def is_moderator(self) -> bool:
        if self.role is None:
            return False
        return self.role is UserRole.MODERATOR
    
    @property
    def full_name(self) -> str:
        """Get user's full name or fallback to username"""
        return self.get_full_name()
    
    @property
    def role_value(self) -> str:
        """Get role as string value"""
        return self.get_role_value()
    
    # =====================================================================
    # BADGE MANAGEMENT METHODS
    # =====================================================================
    
    def add_badge(self, badge):
        """Helper method to add badge to user"""
        if badge not in self.badges:
            self.badges.append(badge)
            badge_count = self.badges.count()
            setattr(self, 'total_badges', badge_count)
            return True
        return False
    
    def remove_badge(self, badge):
        """Helper method to remove badge from user"""
        if badge in self.badges:
            self.badges.remove(badge)
            badge_count = self.badges.count()
            setattr(self, 'total_badges', badge_count)
            return True
        return False
    
    def has_badge(self, badge_id: int) -> bool:
        """Check if user has specific badge"""
        return any(badge.id == badge_id for badge in self.badges)
    
    # =====================================================================
    # REPRESENTATION
    # =====================================================================
    
    def __repr__(self):
        username = str(self.username) if self.username is not None else "Unknown"
        user_id = int(self.id) if self.id is not None else 0  # type: ignore
        tier = self.get_tier_name()
        streak = int(self.current_streak) if self.current_streak is not None else 0  # type: ignore
        return f"<User(id={user_id}, username={username}, tier={tier}, streak={streak})>"

# =====================================================================
# EVENT LISTENERS
# =====================================================================

@event.listens_for(User, "after_insert")
def set_unique_id_after_insert(mapper, connection, target):
    """Generate unique_id after insert"""
    unique_id = getattr(target, 'unique_id', None)
    user_id = getattr(target, 'id', None)
    
    if not unique_id and user_id is not None:
        connection.execute(
            User.__table__.update()
            .where(User.id == user_id)
            .values(unique_id=f"USR-{int(user_id):05d}")  # type: ignore
        )