from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from typing import TYPE_CHECKING, Optional
from ..database.db import Base

class Kamus(Base):
    __tablename__ = "kamus"
    
    # ✅ Category kamus enum
    class CategoryEnum(enum.Enum):
        ALPHABET = "ALPHABET"     # Uppercase untuk match dengan PostgreSQL ENUM
        NUMBERS = "NUMBERS"
        IMBUHAN = "IMBUHAN"
    
    id = Column(Integer, primary_key=True, index=True)
    word_text = Column(String(255), unique=True, index=True, nullable=False)
    definition = Column(Text, nullable=False)
    
    # ✅ Category column dengan uppercase default
    category = Column(
        Enum(CategoryEnum),
        nullable=False,
        default=CategoryEnum.ALPHABET,
        server_default="ALPHABET",  # ✅ Uppercase untuk PostgreSQL
        index=True
    )
    
    image_url_ref = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Kamus(id={self.id}, word_text='{self.word_text}', category='{self.category.value}')>"
    
    # Relation to Soal
    soal_list = relationship(
        "Soal",
        back_populates="kamus_ref",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    @hybrid_property
    def total_soal(self):
        """Get total number of soal related to this kamus entry"""
        try:
            return self.soal_list.count() if self.soal_list else 0
        except:
            return 0
    
    def get_category_display(self) -> str:
        """Get human-readable category name"""
        # ✅ FIX: Use getattr to safely access category value
        category_val = getattr(self, 'category', None)
        
        if category_val is None:
            return "Unknown"
        
        # ✅ Handle both enum instance and string value
        if isinstance(category_val, self.CategoryEnum):
            current_category = category_val
        else:
            # If it's a string, convert to enum
            try:
                current_category = self.CategoryEnum[str(category_val).upper()]
            except (KeyError, AttributeError):
                return str(category_val)
        
        category_map = {
            self.CategoryEnum.ALPHABET: "Alphabet (Huruf/Kata)",
            self.CategoryEnum.NUMBERS: "Numbers (Angka/Bilangan)",
            self.CategoryEnum.IMBUHAN: "Imbuhan (Awalan/Akhiran/Sisipan)"
        }
        return category_map.get(current_category, current_category.value)
    
    # ✅ FIX: Type-safe category check methods
    def is_alphabet(self) -> bool:
        """Check if category is ALPHABET"""
        category_val = getattr(self, 'category', None)
        if category_val is None:
            return False
        
        # Handle both enum and string
        if isinstance(category_val, self.CategoryEnum):
            return category_val == self.CategoryEnum.ALPHABET
        
        return str(category_val).upper() == "ALPHABET"
    
    def is_numbers(self) -> bool:
        """Check if category is NUMBERS"""
        category_val = getattr(self, 'category', None)
        if category_val is None:
            return False
        
        # Handle both enum and string
        if isinstance(category_val, self.CategoryEnum):
            return category_val == self.CategoryEnum.NUMBERS
        
        return str(category_val).upper() == "NUMBERS"
    
    def is_imbuhan(self) -> bool:
        """Check if category is IMBUHAN"""
        category_val = getattr(self, 'category', None)
        if category_val is None:
            return False
        
        # Handle both enum and string
        if isinstance(category_val, self.CategoryEnum):
            return category_val == self.CategoryEnum.IMBUHAN
        
        return str(category_val).upper() == "IMBUHAN"
    
    # ✅ BONUS: Property untuk get category value as string
    @property
    def category_value(self) -> str:
        """Get category value as string"""
        category_val = getattr(self, 'category', None)
        if category_val is None:
            return "ALPHABET"  # Default
        
        if isinstance(category_val, self.CategoryEnum):
            return category_val.value
        
        return str(category_val).upper()