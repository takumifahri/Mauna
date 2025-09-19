from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models.user import User
from ..models.badges import Badge, DificultyLevel
from ..dto.badges_dto import BadgeCreateDTO, BadgeResponseDTO, UserWithBadgesDTO
from ..config.middleware import get_current_user, require_admin, require_moderator_or_admin

router = APIRouter(
    prefix="/badges",
    tags=["Badges"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)

@router.get("/", response_model=List[BadgeResponseDTO])
async def get_all_badges(db: Session = Depends(get_db)):
    """Get all available badges"""
    badges = db.query(Badge).all()
    return badges

@router.post("/", response_model=BadgeResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_badge(
    badge_data: BadgeCreateDTO,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new badge (Admin only)"""
    
    # Check if badge already exists
    existing = db.query(Badge).filter(Badge.nama == badge_data.nama).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Badge with this name already exists"
        )
    
    badge = Badge(
        nama=badge_data.nama,
        deskripsi=badge_data.deskripsi,
        icon=badge_data.icon,
        level=DificultyLevel(badge_data.level)
    )
    
    db.add(badge)
    db.commit()
    db.refresh(badge)
    
    return badge

@router.post("/users/{user_id}/badges/{badge_id}")
async def assign_badge_to_user(
    user_id: int,
    badge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_moderator_or_admin)
):
    """Assign badge to user (Admin/Moderator only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not badge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found")
    
    if user.has_badge(badge_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this badge"
        )
    
    user.add_badge(badge)
    db.commit()
    
    return {
        "success": True,
        "message": f"Badge '{badge.nama}' assigned to user '{user.username}'"
    }

@router.get("/users/{user_id}", response_model=UserWithBadgesDTO)
async def get_user_badges(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all badges for specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nama": user.nama,
        "total_badges": user.total_badges,
        "badges": [
            {
                "badge_id": badge.id,
                "nama": badge.nama,
                "level": badge.level.value,
                "earned_at": None
            }
            for badge in user.badges
        ]
    }

@router.get("/my-badges", response_model=UserWithBadgesDTO)
async def get_my_badges(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's badges"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "nama": current_user.nama,
        "total_badges": current_user.total_badges,
        "badges": [
            {
                "badge_id": badge.id,
                "nama": badge.nama,
                "level": badge.level.value,
                "earned_at": None
            }
            for badge in current_user.badges
        ]
    }