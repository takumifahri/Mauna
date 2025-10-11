from sqlalchemy.orm import Session
from src.models.user import User
from src.models.progress import Progress, ProgressStatus
from src.dto.leaderboard_dto import LeaderboardEntry

TIER_COLORS = {
    "bronze": "#cd7f32",
    "silver": "#c0c0c0",
    "gold": "#ffd700",
    "diamond": "#00bfff",
    "platinum": "#e5e4e2"
}

TIER_THRESHOLDS = {
    "bronze": 10,
    "silver": 30,
    "gold": 90,
    "diamond": 180,
    "platinum": 999999
}
def get_leaderboard(db: Session, limit: int = 20, current_user_id: int = None):
    users = db.query(User).all()
    leaderboard = []
    rank = 1
    for user in users:
        completed_sublevels = db.query(Progress).filter(
            Progress.user_id == user.id,
            Progress.status == ProgressStatus.COMPLETED
        ).count()
        if completed_sublevels >= 3:
            total_xp = user.total_xp or 0
            streak = user.current_streak or 0
            score = total_xp + streak * 2
            current_tier = user.get_tier_name()
            next_tier = current_tier
            for tier, threshold in TIER_THRESHOLDS.items():
                if total_xp >= threshold:
                    next_tier = tier
            if next_tier != current_tier:
                if hasattr(user.tier, "value"):
                    user.tier = type(user.tier)(next_tier)
                else:
                    from src.models.user import UserTier
                    user.tier = UserTier(next_tier)
                db.commit()
            leaderboard.append({
                "user_id": user.id,
                "username": user.username,
                "avatar": user.avatar_url,
                "current_streak": user.current_streak or 0,
                "longest_streak": user.longest_streak or 0,
                "tier": next_tier,
                "tier_color": TIER_COLORS.get(next_tier, "#ccc"),
                "total_xp": total_xp,
                "total_quizzes_completed": user.total_quizzes_completed or 0,
                "total_stars": user.total_badges or 0,
                "completion_rate": 0.0,
                "is_current_user": current_user_id == user.id if current_user_id else False,
                "last_activity_date": str(user.last_activity_date) if user.last_activity_date else None,
                "rank": 0
            })
    leaderboard = sorted(leaderboard, key=lambda x: x["total_xp"] + x["current_streak"] * 2, reverse=True)
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    leaderboard = leaderboard[:limit]
    dto_list = [LeaderboardEntry(**entry) for entry in leaderboard]
    return {
        "success": True,
        "message": "Leaderboard fetched successfully",
        "data": dto_list
    }