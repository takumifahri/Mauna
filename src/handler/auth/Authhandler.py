import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from ...config.hash import hash_password, verify_password
from ...models.user import User, UserRole
from ...config.middleware import auth_manager

# Load environment variables
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
            # Validations
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
            
            # Check existing user
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
            
            # Create user
            hashed_password = hash_password(password)
            
            new_user = User(
                username=username,
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
            
            return {
                "success": True,
                "message": "User registered successfully. Please login to get access token.",
                "data": {
                    "id": new_user.id,
                    "unique_id": new_user.unique_id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "is_active": bool(new_user.is_active),
                    "is_verified": bool(new_user.is_verified),
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
            # Find user
            user = db.query(User).filter(
                (User.email == email_or_username) | (User.username == email_or_username)
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email/username or password"
                )
            
            # Verify password
            if not verify_password(password, str(user.password)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email/username or password"
                )
            
            # Update user status
            if not bool(user.is_active):
                setattr(user, 'is_active', True)
                setattr(user, 'last_login', datetime.utcnow())
                db.commit()
                db.refresh(user)
            else:
                setattr(user, 'last_login', datetime.utcnow())
                db.commit()
            
            # Create token using auth_manager
            access_token_expires = timedelta(minutes=self.auth_manager.access_token_expire_minutes)
            access_token = self.auth_manager.create_access_token(
                data={"sub": str(user.id), "username": user.username, "role": user.role.value},
                expires_delta=access_token_expires
            )
            
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
                    "is_active": bool(user.is_active),
                    "is_verified": bool(user.is_verified),
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
                
            if not bool(user.is_active):
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
        """Get user profile"""
        # Handle datetime serialization
        created_at_str = current_user.created_at.isoformat() if current_user.created_at is not None else None
        updated_at_str = current_user.updated_at.isoformat() if current_user.updated_at is not None else None
        last_login_str = current_user.last_login.isoformat() if current_user.last_login is not None else None
        
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
                "is_active": bool(current_user.is_active),
                "is_verified": bool(current_user.is_verified),
                "avatar": current_user.avatar,
                "bio": current_user.bio,
                "created_at": created_at_str,
                "updated_at": updated_at_str,
                "last_login": last_login_str
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
                "is_active": bool(current_user.is_active),
                "verified_at": datetime.utcnow().isoformat()
            }
        }

# Global auth handler instance
auth_handler = AuthHandler()