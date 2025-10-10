from pydantic import BaseModel, Field
from typing import List, Optional

class TierInfo(BaseModel):
    """Tier information"""
    name: str
    min_streak: int
    max_streak: Optional[int]
    color: str
    display_name: str  # "Bronze", "Silver", etc.

class LeaderboardEntry(BaseModel):
    """Single entry in leaderboard"""
    rank: int
    user_id: int
    username: str
    avatar: Optional[str] = None
    
    # Streak stats
    current_streak: int
    longest_streak: int
    
    # Tier
    tier: str
    tier_color: str  # Instead of emoji
    
    # Additional stats
    total_xp: int = 0
    total_quizzes_completed: int = 0
    total_stars: int = 0
    completion_rate: float = 0.0
    
    # Highlight
    is_current_user: bool = False
    last_activity_date: Optional[str] = None