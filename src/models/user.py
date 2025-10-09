from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from .user_badge import user_badge_association
from ..database.db import Base

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

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
        """Get user ID as Python int - Type-safe accessor"""
        return int(self.id)  # type: ignore
    
    def get_username(self) -> str:
        """Get username as Python str - Type-safe accessor"""
        return str(self.username)
    
    def get_email(self) -> str:
        """Get email as Python str - Type-safe accessor"""
        return str(self.email)
    
    def get_full_name(self) -> str:
        """Get user's full name or fallback to username"""
        return str(self.nama) if self.nama is not None else str(self.username)
    
    def get_role_value(self) -> str:
        """Get role as string value"""
        return self.role.value if self.role is not None else "user"
    
    # Properti hybrid untuk menghasilkan unique_id berdasarkan id
    @hybrid_property
    def generated_unique_id(self):
        return f"USR-{self.id:05d}"
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR
    
    @property
    def full_name(self) -> str:
        """Get user's full name or fallback to username"""
        return str(self.nama) if self.nama is not None else str(self.username)
    
    @property
    def role_value(self) -> str:
        """Get role as string value"""
        return self.role.value if self.role is not None else "user"
    
    def add_badge(self, badge):
        """Helper method to add badge to user"""
        if badge not in self.badges:
            self.badges.append(badge)
            setattr(self, 'total_badges', len(self.badges))
            return True
        return False
    
    def remove_badge(self, badge):
        """Helper method to remove badge from user"""
        if badge in self.badges:
            self.badges.remove(badge)
            setattr(self, 'total_badges', len(self.badges))
            return True
        return False
    
    def has_badge(self, badge_id):
        """Check if user has specific badge"""
        return any(badge.id == badge_id for badge in self.badges)

# Listener untuk mengisi unique_id setelah insert
@event.listens_for(User, "after_insert")
def set_unique_id_after_insert(mapper, connection, target):
    if not target.unique_id:
        connection.execute(
            User.__table__.update()
            .where(User.id == target.id)
            .values(unique_id=f"USR-{target.id:05d}")
        )