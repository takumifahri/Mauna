from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text, Enum, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from ..database.db import Base

class SubLevel(Base):
    __tablename__ = "sublevel"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Remove unique=True karena bisa ada nama sama di level berbeda
    description = Column(Text, nullable=True)
    tujuan = Column(Text, nullable=True)  # Objective of the sublevel
    
    # ✅ Foreign Key ke Level
    level_id = Column(Integer, ForeignKey("level.id"), nullable=False)
    
    # ✅ Many-to-One: SubLevel → Level
    level_ref = relationship(
        "Level",
        back_populates="sublevels",
        lazy="joined"
    )
    
    # ✅ One-to-Many: SubLevel → Soal
    soal_list = relationship(
        "Soal",
        back_populates="sublevel_ref",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # ✅ Add relationship to Progress
    progress_list = relationship(
        "Progress",
        back_populates="sublevel_ref",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # ✅ Add helper methods
    def get_user_progress(self, user_id: int):
        """Get progress for specific user"""
        return self.progress_list.filter_by(user_id=user_id).first()

    def is_unlocked_for_user(self, user_id: int) -> bool:
        """Check if sublevel is unlocked for user"""
        progress = self.get_user_progress(user_id)
        if not progress:
            # Auto-unlock first sublevel in each level
            first_sublevel = self.level_ref.sublevels.order_by('id').first()
            return self.id == first_sublevel.id
        return progress.is_unlocked

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    # Hybrid property untuk count soal
    @hybrid_property
    def total_soal(self):
        return len(self.soal_list.all()) if self.soal_list else 0
    
    # Constraint untuk unique name per level
    __table_args__ = (
        # Unique constraint: name + level_id
        # Artinya nama sublevel boleh sama, tapi tidak boleh sama dalam 1 level
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<SubLevel(id={self.id}, name='{self.name}', level_id={self.level_id}, total_soal={self.total_soal})>"