from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models.user import User, UserRole
from ..dto.user_dto import (
    UserProfileDTO, UserResponse, UserListResponse, UserProfileResponse,
    UserStatsResponse, GenericUserResponse,
    UserRoleUpdateDTO, BulkUserActionDTO
)
from ..config.middleware import get_current_user, require_admin, require_moderator_or_admin
from ..handler.admin.manajemen_user import User_Management

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)

def get_user_management(db: Session = Depends(get_db)) -> User_Management:
    """Dependency untuk mendapatkan User_Management instance"""
    return User_Management(db)

@router.get("/", response_model=Dict[str, Any])
async def get_all_users(
    request: Request,
    limit: int = 100,
    offset: int = 0,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_moderator_or_admin)
):
    """Get all users (Moderator/Admin only)"""
    try:
        result = user_mgmt.get_all_users(limit=limit, offset=offset)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to retrieve users: {str(e)}",
            "data": []
        }

@router.get("/search", response_model=Dict[str, Any])
async def search_users(
    request: Request,
    q: str,
    limit: int = 10,
    offset: int = 0,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_moderator_or_admin)
):
    """Search users by username or email (Moderator/Admin only)"""
    try:
        result = user_mgmt.search_users(query=q, limit=limit, offset=offset)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Search failed: {str(e)}",
            "data": []
        }

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user_by_id(
    user_id: int,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_moderator_or_admin)
):
    """Get user by ID (Moderator/Admin only)"""
    try:
        result = user_mgmt.get_user(user_id)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to retrieve user: {str(e)}",
            "data": None
        }

@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_users_stats(
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_admin)
):
    """Get users statistics (Admin only)"""
    try:
        result = user_mgmt.get_user_statistics()
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to retrieve statistics: {str(e)}",
            "data": {}
        }
        
        
@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: UserRoleUpdateDTO,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_admin)
):
    """Update user role (Admin only)"""
    try:
        # Check if trying to modify own role
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )
        
        result = user_mgmt.update_user_role(user_id, role_data.role)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )

@router.patch("/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_admin)
):
    """Toggle user active status (Admin only)"""
    try:
        # Check if trying to modify own status
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own status"
            )
        
        result = user_mgmt.toggle_user_status(user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle user status: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_admin)
):
    """Delete user (Admin only)"""
    try:
        # Check if trying to delete own account
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        result = user_mgmt.delete_user(user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.get("/{user_id}/badges")
async def get_user_badges(
    user_id: int,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_moderator_or_admin)
):
    """Get user's badges (Moderator/Admin only)"""
    try:
        result = user_mgmt.get_user_badges(user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user badges: {str(e)}"
        )

@router.post("/{user_id}/badges/{badge_id}")
async def assign_badge_to_user(
    user_id: int,
    badge_id: int,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_moderator_or_admin)
):
    """Assign badge to user (Admin/Moderator only)"""
    try:
        result = user_mgmt.assign_badge_to_user(user_id, badge_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User or badge not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign badge: {str(e)}"
        )

@router.delete("/{user_id}/badges/{badge_id}")
async def remove_badge_from_user(
    user_id: int,
    badge_id: int,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_moderator_or_admin)
):
    """Remove badge from user (Admin/Moderator only)"""
    try:
        result = user_mgmt.remove_badge_from_user(user_id, badge_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User, badge not found or user doesn't have this badge"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove badge: {str(e)}"
        )

@router.post("/bulk-actions/activate")
async def bulk_activate_users(
    bulk_data: BulkUserActionDTO,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_admin)
):
    """Bulk activate users (Admin only)"""
    try:
        # Remove current user ID if present
        user_ids = [uid for uid in bulk_data.user_ids if uid != current_user.id]
        
        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid user IDs provided"
            )
        
        result = user_mgmt.bulk_activate_users(user_ids)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk activation failed: {str(e)}"
        )

@router.post("/bulk-actions/deactivate")
async def bulk_deactivate_users(
    bulk_data: BulkUserActionDTO,
    request: Request,
    user_mgmt: User_Management = Depends(get_user_management),
    current_user: User = Depends(require_admin)
):
    """Bulk deactivate users (Admin only)"""
    try:
        # Remove current user ID if present
        user_ids = [uid for uid in bulk_data.user_ids if uid != current_user.id]
        
        if not user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid user IDs provided"
            )
        
        result = user_mgmt.bulk_deactivate_users(user_ids)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk deactivation failed: {str(e)}"
        )

# Juga perbaiki get_current_user_profile untuk konversi manual:
@router.get("/me", response_model=UserProfileDTO)
async def get_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    # Convert SQLAlchemy model to dict first
    user_dict = {
        "id": current_user.id,
        "unique_id": current_user.unique_id or f"USR-{current_user.id:05d}",
        "username": current_user.username,
        "email": current_user.email,
        "nama": current_user.nama,
        "telpon": current_user.telpon,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        "is_active": bool(current_user.is_active),
        "is_verified": bool(current_user.is_verified),
        "avatar": current_user.avatar,
        "bio": current_user.bio,
        "total_badges": current_user.total_badges or 0
    }
    return UserProfileDTO.model_validate(user_dict)