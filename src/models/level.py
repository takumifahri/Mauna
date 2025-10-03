from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text, Enum, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from ..database.db import Base

class Level(Base):
    __tablename__ = "level"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    tujuan = Column(Text, nullable=True)  # Objective of the level
    
    # ✅ One-to-Many: Level → SubLevel
    sublevels = relationship(
        "SubLevel",
        back_populates="level_ref",
        cascade="all, delete-orphan",
        lazy="dynamic"  # For better performance with many sublevels
    )
    
    # Hybrid property untuk count sublevels
    @hybrid_property
    def total_sublevels(self):
        return len(self.sublevels.all()) if self.sublevels else 0
    
    def __repr__(self):
        return f"<Level(id={self.id}, name='{self.name}', sublevels={self.total_sublevels})>"