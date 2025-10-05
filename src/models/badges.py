from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database.db import Base

class DificultyLevel(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    
class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(255), unique=True, index=True, nullable=False)
    deskripsi = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)  # URL or path to icon image
    level = Column(Enum(DificultyLevel), default=DificultyLevel.EASY)
    
    # Relasi many-to-many dengan User
    users = relationship(
        "User",
        secondary="user_badges",  # menggunakan nama tabel langsung
        back_populates="badges"
    )
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    def __repr__(self):
        return f"<Badge(id={self.id}, nama={self.nama}, level={self.level})>"