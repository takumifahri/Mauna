from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime
from ..database import Base

class TokenBlacklist(Base):
    """Model untuk menyimpan revoked JWT tokens"""
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # Token expiry time
    reason = Column(String, nullable=True)  # Optional: logout, password_change, etc.
    
    # Index untuk query cepat
    __table_args__ = (
        Index('ix_token_user_id', 'user_id'),
        Index('ix_token_expires_at', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<TokenBlacklist(id={self.id}, user_id={self.user_id}, revoked_at={self.revoked_at})>"