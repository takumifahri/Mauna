import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import uuid

from ...config.hash import hash_password, verify_password
from ...models.user import User, UserRole
from ...config.middleware import auth_manager

load_dotenv()

class AuthHandler:
    """Authentication handler for business logic only"""
    
    def __init__(self):
        self.auth_manager = auth_manager
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    async def register(self, username: str, email: str, password: str, nama: str = None, db: Session = None) -> Dict[str, Any]:
        """Register new user"""
        if db is None:
            raise ValueError("Database session is required")
            
        try:
            if not self.validate_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            
            password_validation = self.validate_password(password)
            if not password_validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Password validation failed", 
                        "errors": password_validation["errors"]
                    }
                )
            
            existing_user = db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                if str(existing_user.email) == email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
            
            hashed_password = hash_password(password)
            unique_id = str(uuid.uuid4())
            
            new_user = User(
                username=username,
                unique_id=unique_id,
                email=email,
                password=hashed_password,
                nama=nama,
                role=UserRole.USER,
                is_active=False,
                is_verified=False
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # ✅ Type-safe boolean check
            is_active_val = getattr(new_user, 'is_active', None)
            is_verified_val = getattr(new_user, 'is_verified', None)
            
            return {
                "success": True,
                "message": "User registered successfully. Please login to get access token.",
                "data": {
                    "id": new_user.id,
                    "unique_id": new_user.unique_id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "is_active": bool(is_active_val) if is_active_val is not None else False,
                    "is_verified": bool(is_verified_val) if is_verified_val is not None else False,
                    "next_step": "Please use /api/auth/login to get your access token"
                }
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
            
    async def login(self, email_or_username: str, password: str, db: Session = None) -> Dict[str, Any]:
        """Login user"""
        if db is None:
            raise ValueError("Database session is required")
            
        try:
            user = db.query(User).filter(
                (User.email == email_or_username) | (User.username == email_or_username)
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email/username or password"
                )
            
            if not verify_password(password, str(user.password)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email/username or password"
                )
            
            # ✅ FIX: Type-safe is_active check
            is_active_val = getattr(user, 'is_active', None)
            if is_active_val is None or not bool(is_active_val):
                setattr(user, 'is_active', True)
                setattr(user, 'last_login', datetime.utcnow())
                db.commit()
                db.refresh(user)
            else:
                setattr(user, 'last_login', datetime.utcnow())
                db.commit()
            
            access_token_expires = timedelta(minutes=self.auth_manager.access_token_expire_minutes)
            access_token = self.auth_manager.create_access_token(
                data={"sub": str(user.id), "username": user.username, "role": user.role.value},
                expires_delta=access_token_expires
            )
            
            # ✅ Generate avatar_url dynamically
            avatar = getattr(user, 'avatar', None)
            avatar_url = f"/{avatar}" if avatar is not None and avatar != "" else None
            
            return {
                "success": True,
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.auth_manager.access_token_expire_minutes * 60,
                "data": {
                    "id": user.id,
                    "unique_id": user.unique_id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "avatar": avatar,
                    "avatar_url": avatar_url,
                    "is_active": bool(getattr(user, 'is_active', False)),
                    "is_verified": bool(getattr(user, 'is_verified', False)),
                    "last_login": user.last_login.isoformat() if user.last_login is not None else None
                }
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )
    
    async def logout(self, current_user: User, db: Session = None) -> Dict[str, Any]:
        """Logout user"""
        if db is None:
            raise ValueError("Database session is required")
            
        try:
            setattr(current_user, 'is_active', False)
            db.commit()
            
            return {
                "success": True,
                "message": f"User {current_user.username} logged out successfully",
                "data": {
                    "detail": "User status set to inactive",
                    "logged_out_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Logout failed: {str(e)}"
            )
    
    async def refresh_token(self, token: str, db: Session = None) -> Dict[str, Any]:
        """Refresh JWT token"""
        if db is None:
            raise ValueError("Database session is required")
            
        try:
            payload = self.auth_manager.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
                
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # ✅ FIX: Type-safe is_active check
            is_active_val = getattr(user, 'is_active', None)
            if is_active_val is None or not bool(is_active_val):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
                
            new_token = self.auth_manager.create_access_token(
                data={"sub": user_id, "username": user.username, "role": user.role.value},
                expires_delta=timedelta(minutes=self.auth_manager.access_token_expire_minutes)
            )
            
            return {
                "success": True,
                "message": "Token refreshed successfully",
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": self.auth_manager.access_token_expire_minutes * 60
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token refresh failed: {str(e)}"
            )
    
    async def get_profile(self, current_user: User) -> Dict[str, Any]:
        """Get user profile with gamification stats"""
        created_at_str = current_user.created_at.isoformat() if current_user.created_at is not None else None
        updated_at_str = current_user.updated_at.isoformat() if current_user.updated_at is not None else None
        last_login_str = current_user.last_login.isoformat() if current_user.last_login is not None else None
        
        # ✅ Generate avatar_url dynamically
        avatar = getattr(current_user, 'avatar', None)
        avatar_url = f"/{avatar}" if avatar is not None and avatar != "" else None
        
        return {
            "success": True,
            "message": "Profile retrieved successfully",
            "data": {
                "id": current_user.id,
                "unique_id": current_user.unique_id,
                "username": current_user.username,
                "email": current_user.email,
                "nama": current_user.nama,
                "telpon": current_user.telpon,
                "role": current_user.role.value,
                "is_active": bool(getattr(current_user, 'is_active', False)),
                "is_verified": bool(getattr(current_user, 'is_verified', False)),
                "avatar": avatar,
                "avatar_url": avatar_url,
                "bio": current_user.bio,
                "created_at": created_at_str,
                "updated_at": updated_at_str,
                "last_login": last_login_str,
                # Gamification stats
                "current_streak": getattr(current_user, 'current_streak', 0),
                "longest_streak": getattr(current_user, 'longest_streak', 0),
                "tier": current_user.get_tier_name(),
                "tier_color": current_user.get_tier_color(),
                "total_xp": getattr(current_user, 'total_xp', 0),
                "total_quizzes_completed": getattr(current_user, 'total_quizzes_completed', 0),
                "total_badges": getattr(current_user, 'total_badges', 0)
            }
        }
    
    async def verify_auth(self, current_user: User) -> Dict[str, Any]:
        """Verify authentication"""
        return {
            "success": True,
            "message": "Token is valid",
            "data": {
                "authenticated": True,
                "user_id": current_user.id,
                "username": current_user.username,
                "role": current_user.role.value,
                "is_active": bool(getattr(current_user, 'is_active', False)),
                "verified_at": datetime.utcnow().isoformat()
            }
        }

    async def update_profile(
        self, 
        current_user: User, 
        nama: Optional[str] = None,
        telpon: Optional[str] = None,
        bio: Optional[str] = None,
        username: Optional[str] = None,
        avatar_file: Optional[UploadFile] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Update user profile - all fields optional including avatar
        """
        if db is None:
            raise ValueError("Database session is required")
        
        try:
            # ✅ FIX: Re-attach user to session if detached
            if not db.is_active or current_user not in db:
                current_user = db.merge(current_user)
            
            updated_fields = []
            
            # Update username if provided
            if username is not None and username.strip():
                existing_username = db.query(User).filter(
                    User.username == username,
                    User.id != current_user.id
                ).first()
                
                if existing_username:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
                
                setattr(current_user, 'username', username.strip())
                updated_fields.append("username")
            
            # Update nama if provided
            if nama is not None and nama.strip():
                setattr(current_user, 'nama', nama.strip())
                updated_fields.append("nama")
            
            # Update telpon if provided
            if telpon is not None:
                telpon_clean = re.sub(r'\D', '', telpon)
                if len(telpon_clean) < 10 or len(telpon_clean) > 15:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid phone number format"
                    )
                setattr(current_user, 'telpon', telpon_clean)
                updated_fields.append("telpon")
            
            # Update bio if provided
            if bio is not None:
                setattr(current_user, 'bio', bio.strip() if bio.strip() else None)
                updated_fields.append("bio")
            
            # ✅ Update avatar if provided
            if avatar_file is not None and avatar_file.filename:
                from ...utils.FileHandler import STORAGE_FOLDERS, _ensure_dir_exists, save_image
                
                # Ensure avatars folder exists
                avatar_folder = os.path.join(STORAGE_FOLDERS.get("soal", "").replace("soal", ""), "avatars")
                _ensure_dir_exists(avatar_folder)
                STORAGE_FOLDERS["avatars"] = avatar_folder
                
                # Save new avatar
                avatar_path = save_image(avatar_file, "avatars")
                
                # ✅ FIX: Re-query user after file operation to ensure session attachment
                user_id = current_user.id
                current_user = db.query(User).filter(User.id == user_id).first()
                
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found after avatar upload"
                    )
                
                # Delete old avatar if exists
                old_avatar = getattr(current_user, 'avatar', None)
                if old_avatar is not None and old_avatar != "":
                    old_avatar_path = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)),
                        old_avatar.replace("storage/", "")
                    )
                    if os.path.exists(old_avatar_path):
                        try:
                            os.remove(old_avatar_path)
                        except Exception as e:
                            print(f"Warning: Could not delete old avatar: {e}")
                
                # Update user avatar
                setattr(current_user, 'avatar', avatar_path)
                updated_fields.append("avatar")
            
            if not updated_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            # ✅ Update timestamp before commit
            setattr(current_user, 'updated_at', datetime.utcnow())
            
            # ✅ FIX: Ensure user is in session before commit
            db.add(current_user)
            db.commit()
            db.refresh(current_user)
            
            # ✅ Generate avatar_url
            avatar = getattr(current_user, 'avatar', None)
            avatar_url = f"/{avatar}" if avatar is not None and avatar != "" else None
            
            return {
                "success": True,
                "message": f"Profile updated successfully. Updated fields: {', '.join(updated_fields)}",
                "data": {
                    "id": current_user.id,
                    "unique_id": current_user.unique_id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "nama": current_user.nama,
                    "telpon": current_user.telpon,
                    "bio": current_user.bio,
                    "avatar": avatar,
                    "avatar_url": avatar_url,
                    "updated_fields": updated_fields,
                    "updated_at": current_user.updated_at.isoformat() if current_user.updated_at is not None else None
                }
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Profile update failed: {str(e)}"
            )
    async def change_password(
        self, 
        current_user: User, 
        old_password: str,
        new_password: str,
        confirm_password: str,
        db: Session = None
    ) -> Dict[str, Any]:
        """Change user password"""
        if db is None:
            raise ValueError("Database session is required")
        
        try:
            if not verify_password(old_password, str(current_user.password)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )
            
            if new_password != confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password and confirmation do not match"
                )
            
            password_validation = self.validate_password(new_password)
            if not password_validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Password validation failed",
                        "errors": password_validation["errors"]
                    }
                )
            
            if verify_password(new_password, str(current_user.password)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password must be different from current password"
                )
            
            hashed_password = hash_password(new_password)
            setattr(current_user, 'password', hashed_password)
            setattr(current_user, 'updated_at', datetime.utcnow())
            
            db.commit()
            
            return {
                "success": True,
                "message": "Password changed successfully",
                "data": {
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "changed_at": datetime.utcnow().isoformat(),
                    "note": "Please login again with your new password"
                }
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password change failed: {str(e)}"
            )
    
    async def delete_avatar(
        self, 
        current_user: User,
        db: Session = None
    ) -> Dict[str, Any]:
        """Delete user avatar"""
        if db is None:
            raise ValueError("Database session is required")
        
        try:
            # ✅ FIX: Type-safe avatar check
            avatar_val = getattr(current_user, 'avatar', None)
            if avatar_val is None or avatar_val == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No avatar to delete"
                )
            
            avatar_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                avatar_val.replace("storage/", "")
            )
            
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                except Exception as e:
                    print(f"Warning: Could not delete avatar file: {e}")
            
            setattr(current_user, 'avatar', None)
            setattr(current_user, 'updated_at', datetime.utcnow())
            
            db.commit()
            db.refresh(current_user)
            
            return {
                "success": True,
                "message": "Avatar deleted successfully",
                "data": {
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "avatar": None,
                    "avatar_url": None,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Avatar deletion failed: {str(e)}"
            )

# Global instance
auth_handler = AuthHandler()