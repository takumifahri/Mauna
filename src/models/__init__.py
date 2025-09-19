# Import models dalam urutan yang benar untuk menghindari circular imports
from .user_badge import user_badge_association  # Import tabel asosiatif dulu
from .user import User, UserRole
from .badges import Badge

# Export untuk kemudahan import
__all__ = [
    'user_badge_association',
    'User',
    'UserRole', 
    'Badge',
]