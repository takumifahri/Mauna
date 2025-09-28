from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from ..database.db import Base

# Tabel asosiatif untuk relasi many-to-many antara User dan Badge
user_badge_association = Table(
    "user_badges",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("badge_id", Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False),
    Column("earned_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    
    # Constraints
    UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),  # Mencegah duplikasi
    
    # Indexes untuk performance
    Index("idx_user_badges_user_id", "user_id"),
    Index("idx_user_badges_badge_id", "badge_id"),
    Index("idx_user_badges_earned_at", "earned_at"),
    Index("idx_user_badges_user_earned", "user_id", "earned_at"),  # Composite index
)

# Note: Relationships didefinisikan di model User dan Badge, bukan di sini