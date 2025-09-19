import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from dotenv import load_dotenv

from ...config.hash import hash_password, verify_password
from ...models.user import User, UserRole
from ...models.badges import Badge
from ...dto.user_dto import (
    UserDataDTO, UserListDataDTO, UserProfileDataDTO,
    UserResponse, UserListResponse, UserProfileResponse,
    UserStatsResponse, GenericUserResponse
)

load_dotenv()

class User_Management:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID with consistent response format"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {
                "success": False,
                "message": f"User with ID {user_id} not found",
                "data": None
            }
        
        # Convert SQLAlchemy model to dict first, then to Pydantic
        user_dict = {
            "id": user.id,
            "unique_id": user.unique_id or f"USR-{user.id:05d}",
            "username": user.username,
            "email": user.email,
            "nama": user.nama,
            "telpon": user.telpon,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "is_active": bool(user.is_active),
            "is_verified": bool(user.is_verified),
            "avatar": user.avatar,
            "bio": user.bio,
            "total_badges": user.total_badges or 0,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login
        }
        
        return {
            "success": True,
            "message": "User retrieved successfully",
            "data": UserDataDTO.model_validate(user_dict).model_dump()
        }

    def get_all_users(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get all users with pagination and consistent response format"""
        try:
            users = self.db.query(User).offset(offset).limit(limit).all()
            total_count = self.db.query(User).count()
            
            result = []
            for user in users:
                user_dict = {
                    "id": user.id,
                    "unique_id": user.unique_id or f"USR-{user.id:05d}",
                    "username": user.username,
                    "email": user.email,
                    "nama": user.nama,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "is_active": bool(user.is_active),
                    "is_verified": bool(user.is_verified),
                    "total_badges": user.total_badges or 0,
                    "created_at": user.created_at
                }
                result.append(UserListDataDTO.model_validate(user_dict).model_dump())
            
            return {
                "success": True,
                "message": f"Retrieved {len(result)} users successfully",
                "data": result,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": (offset + limit) < total_count,
                    "has_prev": offset > 0
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve users: {str(e)}",
                "data": []
            }

    def search_users(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Search users by username or email with consistent response format"""
        try:
            users = self.db.query(User).filter(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.nama.ilike(f"%{query}%")
                )
            ).offset(offset).limit(limit).all()
            
            total_count = self.db.query(User).filter(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.nama.ilike(f"%{query}%")
                )
            ).count()
            
            result = []
            for user in users:
                user_dict = {
                    "id": user.id,
                    "unique_id": user.unique_id or f"USR-{user.id:05d}",
                    "username": user.username,
                    "email": user.email,
                    "nama": user.nama,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "is_active": bool(user.is_active),
                    "is_verified": bool(user.is_verified),
                    "total_badges": user.total_badges or 0,
                    "created_at": user.created_at
                }
                result.append(UserListDataDTO.model_validate(user_dict).model_dump())
            
            return {
                "success": True,
                "message": f"Found {len(result)} users matching '{query}'",
                "data": result,
                "search": {
                    "query": query,
                    "total_found": total_count,
                    "limit": limit,
                    "offset": offset
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Search failed: {str(e)}",
                "data": []
            }

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user with consistent response format"""
        try:
            # Hash password if provided
            if 'password' in user_data:
                user_data['password'] = hash_password(user_data['password'])
            
            new_user = User(**user_data)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            # Convert to dict for Pydantic
            user_dict = {
                "id": new_user.id,
                "unique_id": new_user.unique_id or f"USR-{new_user.id:05d}",
                "username": new_user.username,
                "email": new_user.email,
                "nama": new_user.nama,
                "telpon": new_user.telpon,
                "role": new_user.role.value if hasattr(new_user.role, 'value') else str(new_user.role),
                "is_active": bool(new_user.is_active),
                "is_verified": bool(new_user.is_verified),
                "avatar": new_user.avatar,
                "bio": new_user.bio,
                "total_badges": new_user.total_badges or 0,
                "created_at": new_user.created_at,
                "updated_at": new_user.updated_at,
                "last_login": new_user.last_login
            }
            
            return {
                "success": True,
                "message": f"User '{new_user.username}' created successfully",
                "data": UserDataDTO.model_validate(user_dict).model_dump()
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to create user: {str(e)}",
                "data": None
            }

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }
            
            # Store original values for comparison
            original_username = user.username
            
            for key, value in user_data.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            
            setattr(user, 'updated_at', datetime.utcnow())
            self.db.commit()
            self.db.refresh(user)
            
            # Convert to dict for Pydantic
            user_dict = {
                "id": user.id,
                "unique_id": user.unique_id or f"USR-{user.id:05d}",
                "username": user.username,
                "email": user.email,
                "nama": user.nama,
                "telpon": user.telpon,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "is_active": bool(user.is_active),
                "is_verified": bool(user.is_verified),
                "avatar": user.avatar,
                "bio": user.bio,
                "total_badges": user.total_badges or 0,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login
            }
            
            return {
                "success": True,
                "message": f"User '{original_username}' updated successfully",
                "data": UserDataDTO.model_validate(user_dict).model_dump()
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to update user: {str(e)}",
                "data": None
            }

    def update_user_role(self, user_id: int, new_role: str) -> Dict[str, Any]:
        """Update user role with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }
            
            old_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            
            try:
                role_enum = UserRole(new_role)
                setattr(user, 'role', role_enum)
                setattr(user, 'updated_at', datetime.utcnow())
                self.db.commit()
                self.db.refresh(user)
                
                return {
                    "success": True,
                    "message": f"User role updated from '{old_role}' to '{role_enum.value}'",
                    "data": {
                        "user_id": user.id,
                        "username": user.username,
                        "old_role": old_role,
                        "new_role": role_enum.value,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            except ValueError:
                return {
                    "success": False,
                    "message": f"Invalid role value: {new_role}",
                    "data": None
                }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to update user role: {str(e)}",
                "data": None
            }

    def toggle_user_status(self, user_id: int) -> Dict[str, Any]:
        """Toggle user active status with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }
            
            current_status = bool(user.is_active)
            new_status = not current_status
            
            setattr(user, 'is_active', new_status)
            setattr(user, 'updated_at', datetime.utcnow())
            self.db.commit()
            self.db.refresh(user)
            
            status_text = "activated" if new_status else "deactivated"
            
            return {
                "success": True,
                "message": f"User '{user.username}' {status_text} successfully",
                "data": {
                    "user_id": user.id,
                    "username": user.username,
                    "old_status": current_status,
                    "new_status": new_status,
                    "status_text": status_text,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to toggle user status: {str(e)}",
                "data": None
            }

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete user with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }
            
            username = str(user.username)
            self.db.delete(user)
            self.db.commit()
            
            return {
                "success": True,
                "message": f"User '{username}' deleted successfully",
                "data": {
                    "deleted_user_id": user_id,
                    "deleted_username": username,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to delete user: {str(e)}",
                "data": None
            }

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }
            
            # Convert to dict for Pydantic
            profile_dict = {
                "id": user.id,
                "unique_id": user.unique_id or f"USR-{user.id:05d}",
                "username": user.username,
                "email": user.email,
                "nama": user.nama,
                "telpon": user.telpon,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "is_active": bool(user.is_active),
                "is_verified": bool(user.is_verified),
                "avatar": user.avatar,
                "bio": user.bio,
                "total_badges": user.total_badges or 0,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login
            }
            
            return {
                "success": True,
                "message": f"Profile for user '{user.username}' retrieved successfully",
                "data": UserProfileDataDTO.model_validate(profile_dict).model_dump()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve user profile: {str(e)}",
                "data": None
            }

    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics with consistent response format"""
        try:
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active.is_(True)).count()
            verified_users = self.db.query(User).filter(User.is_verified.is_(True)).count()
            admin_count = self.db.query(User).filter(User.role == UserRole.ADMIN).count()
            moderator_count = self.db.query(User).filter(User.role == UserRole.MODERATOR).count()
            user_count = self.db.query(User).filter(User.role == UserRole.USER).count()
            
            # Get recent registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = self.db.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()
            
            stats_data = {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "inactive_users": total_users - active_users,
                "unverified_users": total_users - verified_users,
                "recent_registrations": recent_registrations,
                "roles": {
                    "admin": admin_count,
                    "moderator": moderator_count,
                    "user": user_count
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "message": "User statistics retrieved successfully",
                "data": stats_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve user statistics: {str(e)}",
                "data": {}
            }

    def bulk_activate_users(self, user_ids: List[int]) -> Dict[str, Any]:
        """Bulk activate users with consistent response format"""
        try:
            users = self.db.query(User).filter(User.id.in_(user_ids)).all()
            
            if not users:
                return {
                    "success": False,
                    "message": "No users found with provided IDs",
                    "data": {
                        "processed_count": 0,
                        "activated_count": 0,
                        "user_ids": user_ids
                    }
                }
            
            activated_count = 0
            activated_users = []
            
            for user in users:
                if not bool(user.is_active):
                    setattr(user, 'is_active', True)
                    setattr(user, 'updated_at', datetime.utcnow())
                    activated_count += 1
                    activated_users.append({
                        "id": user.id,
                        "username": user.username
                    })
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Successfully activated {activated_count} out of {len(users)} users",
                "data": {
                    "total_processed": len(users),
                    "activated_count": activated_count,
                    "skipped_count": len(users) - activated_count,
                    "activated_users": activated_users,
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Bulk activation failed: {str(e)}",
                "data": {
                    "processed_count": 0,
                    "activated_count": 0,
                    "user_ids": user_ids
                }
            }

    def bulk_deactivate_users(self, user_ids: List[int]) -> Dict[str, Any]:
        """Bulk deactivate users with consistent response format"""
        try:
            users = self.db.query(User).filter(User.id.in_(user_ids)).all()
            
            if not users:
                return {
                    "success": False,
                    "message": "No users found with provided IDs",
                    "data": {
                        "processed_count": 0,
                        "deactivated_count": 0,
                        "user_ids": user_ids
                    }
                }
            
            deactivated_count = 0
            deactivated_users = []
            
            for user in users:
                if bool(user.is_active):
                    setattr(user, 'is_active', False)
                    setattr(user, 'updated_at', datetime.utcnow())
                    deactivated_count += 1
                    deactivated_users.append({
                        "id": user.id,
                        "username": user.username
                    })
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Successfully deactivated {deactivated_count} out of {len(users)} users",
                "data": {
                    "total_processed": len(users),
                    "deactivated_count": deactivated_count,
                    "skipped_count": len(users) - deactivated_count,
                    "deactivated_users": deactivated_users,
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Bulk deactivation failed: {str(e)}",
                "data": {
                    "processed_count": 0,
                    "deactivated_count": 0,
                    "user_ids": user_ids
                }
            }
            

    def get_user_badges(self, user_id: int) -> Dict[str, Any]:
        """Get user's badges with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": []
                }
            
            # Get user badges
            badges_data = []
            for badge in user.badges:
                badge_dict = {
                    "badge_id": badge.id,
                    "nama": badge.nama,
                    "deskripsi": badge.deskripsi,
                    "icon": badge.icon,
                    "level": badge.level.value if hasattr(badge.level, 'value') else str(badge.level),
                    "earned_at": None  # You might want to add earned_at timestamp to your model
                }
                badges_data.append(badge_dict)
            
            return {
                "success": True,
                "message": f"Retrieved {len(badges_data)} badges for user '{user.username}'",
                "data": {
                    "user_id": user.id,
                    "username": user.username,
                    "total_badges": len(badges_data),
                    "badges": badges_data
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve user badges: {str(e)}",
                "data": []
            }

    def assign_badge_to_user(self, user_id: int, badge_id: int) -> Dict[str, Any]:
        """Assign badge to user with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            badge = self.db.query(Badge).filter(Badge.id == badge_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }
            
            if not badge:
                return {
                    "success": False,
                    "message": f"Badge with ID {badge_id} not found",
                    "data": None
                }
            
            # Check if user already has this badge
            if badge in user.badges:
                return {
                    "success": False,
                    "message": f"User '{user.username}' already has badge '{badge.nama}'",
                    "data": {
                        "user_id": user.id,
                        "username": user.username,
                        "badge_id": badge.id,
                        "badge_name": badge.nama,
                        "already_assigned": True
                    }
                }
            
            # Assign badge to user
            user.badges.append(badge)
            
            # Update total_badges count if you have this field
            if hasattr(user, 'total_badges'):
                setattr(user, 'total_badges', len(user.badges))
            
            setattr(user, 'updated_at', datetime.utcnow())
            self.db.commit()
            self.db.refresh(user)
            
            return {
                "success": True,
                "message": f"Badge '{badge.nama}' successfully assigned to user '{user.username}'",
                "data": {
                    "user_id": user.id,
                    "username": user.username,
                    "badge_id": badge.id,
                    "badge_name": badge.nama,
                    "badge_level": badge.level.value if hasattr(badge.level, 'value') else str(badge.level),
                    "total_user_badges": len(user.badges),
                    "assigned_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to assign badge: {str(e)}",
                "data": None
            }

    def remove_badge_from_user(self, user_id: int, badge_id: int) -> Dict[str, Any]:
        """Remove badge from user with consistent response format"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            badge = self.db.query(Badge).filter(Badge.id == badge_id).first()
            
            if not user:
                return {
                    "success": False,
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }
            
            if not badge:
                return {
                    "success": False,
                    "message": f"Badge with ID {badge_id} not found",
                    "data": None
                }
            
            # Check if user has this badge
            if badge not in user.badges:
                return {
                    "success": False,
                    "message": f"User '{user.username}' doesn't have badge '{badge.nama}'",
                    "data": {
                        "user_id": user.id,
                        "username": user.username,
                        "badge_id": badge.id,
                        "badge_name": badge.nama,
                        "not_assigned": True
                    }
                }
            
            # Remove badge from user
            user.badges.remove(badge)
            
            # Update total_badges count if you have this field
            if hasattr(user, 'total_badges'):
                setattr(user, 'total_badges', len(user.badges))
            
            setattr(user, 'updated_at', datetime.utcnow())
            self.db.commit()
            self.db.refresh(user)
            
            return {
                "success": True,
                "message": f"Badge '{badge.nama}' successfully removed from user '{user.username}'",
                "data": {
                    "user_id": user.id,
                    "username": user.username,
                    "badge_id": badge.id,
                    "badge_name": badge.nama,
                    "badge_level": badge.level.value if hasattr(badge.level, 'value') else str(badge.level),
                    "total_user_badges": len(user.badges),
                    "removed_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to remove badge: {str(e)}",
                "data": None
            }

    # Method untuk mendapatkan semua badges yang tersedia
    def get_available_badges(self) -> Dict[str, Any]:
        """Get all available badges with consistent response format"""
        try:
            badges = self.db.query(Badge).all()
            
            badges_data = []
            for badge in badges:
                badge_dict = {
                    "id": badge.id,
                    "nama": badge.nama,
                    "deskripsi": badge.deskripsi,
                    "icon": badge.icon,
                    "level": badge.level.value if hasattr(badge.level, 'value') else str(badge.level),
                    "created_at": badge.created_at.isoformat() if hasattr(badge, 'created_at') and badge.created_at is not None else None
                }
                badges_data.append(badge_dict)
            
            return {
                "success": True,
                "message": f"Retrieved {len(badges_data)} available badges",
                "data": badges_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve available badges: {str(e)}",
                "data": []
            }

    # Method untuk mendapatkan users yang memiliki badge tertentu
    def get_users_with_badge(self, badge_id: int) -> Dict[str, Any]:
        """Get users who have specific badge with consistent response format"""
        try:
            badge = self.db.query(Badge).filter(Badge.id == badge_id).first()
            
            if not badge:
                return {
                    "success": False,
                    "message": f"Badge with ID {badge_id} not found",
                    "data": []
                }
            
            users_data = []
            for user in badge.users:  # Assuming you have a relationship set up
                user_dict = {
                    "id": user.id,
                    "unique_id": user.unique_id or f"USR-{user.id:05d}",
                    "username": user.username,
                    "email": user.email,
                    "nama": user.nama,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "is_active": bool(user.is_active),
                    "earned_at": None  # You might want to add this timestamp
                }
                users_data.append(user_dict)
            
            return {
                "success": True,
                "message": f"Found {len(users_data)} users with badge '{badge.nama}'",
                "data": {
                    "badge_id": badge.id,
                    "badge_name": badge.nama,
                    "badge_level": badge.level.value if hasattr(badge.level, 'value') else str(badge.level),
                    "total_users": len(users_data),
                    "users": users_data
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve users with badge: {str(e)}",
                "data": []
            }