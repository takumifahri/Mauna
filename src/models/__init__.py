"""
Models package for SMT 5 application.
"""

from .user import User, UserRole

# Import semua models di sini agar Alembic bisa detect
__all__ = [
    'User',
    'UserRole'
]