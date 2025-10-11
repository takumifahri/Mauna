from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text, Enum, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from ..database.db import Base

class Soal(Base):
    __tablename__ = "soal"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    video_url = Column(Text, nullable=True)  # URL to a related video
    image_url = Column(Text, nullable=True)  # URL to question image
    
    # ✅ Foreign Key ke Kamus (Dictionary)
    dictionary_id = Column(Integer, ForeignKey("kamus.id"), nullable=False)
    point_gamifikasi = Column(Integer, default=1)  # Points for gamification
    # ✅ Foreign Key ke SubLevel  
    sublevel_id = Column(Integer, ForeignKey("sublevel.id"), nullable=False)
    
    # ✅ Many-to-One: Soal → Kamus
    kamus_ref = relationship(
        "Kamus",  # Fixed: should be "Kamus" not "kamus"
        back_populates="soal_list",
        lazy="joined"
    )
    
    # ✅ Many-to-One: Soal → SubLevel
    sublevel_ref = relationship(
        "SubLevel",
        back_populates="soal_list",
        lazy="joined"
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    # Hybrid property untuk mendapatkan level dari sublevel
    @hybrid_property
    def level_name(self):
        return self.sublevel_ref.level_ref.name if self.sublevel_ref and self.sublevel_ref.level_ref else None
    
    @hybrid_property
    def sublevel_name(self):
        return self.sublevel_ref.name if self.sublevel_ref else None
    
    def __repr__(self):
        return f"<Soal(id={self.id}, question='{self.question[:30]}...', sublevel='{self.sublevel_name}')>"