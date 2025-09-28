from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from ..database.db import Base

class kamus(Base):
    __tablename__ = "kamus"
    
    id = Column(Integer, primary_key=True, index=True)
    word_text = Column(String(255), unique=True, index=True, nullable=False)
    definition = Column(Text, nullable=False)
    
    image_url_ref = Column(String(255), nullable=True)  # URL to an image
    video_url = Column(String(255), nullable=True)  # URL to a related video
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    def __repr__(self):
        return f"<kamus(id={self.id}, word_text={self.word_text})>"
    
    # Relation to Soal
    soal = relationship(
        "Soal",
        back_populates="kamus_ref",
        foreign_keys="[Soal.dictionary_id]",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )