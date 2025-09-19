from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
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
    # Unique constraint untuk mencegah duplikasi badge pada user yang sama
    # UniqueConstraint("user_id", "badge_id", name="unique_user_badge")
)