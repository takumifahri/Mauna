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
    dictionary_id = Column(Integer, ForeignKey("kamus.id"), nullable=False)
    video_url = Column(Text, nullable=True)  # URL to a related video
    # Relationship to Kamus
    kamus_ref = relationship(
        "kamus",
        back_populates="soal",
        foreign_keys="[Soal.dictionary_id]",
        lazy="joined"
    )