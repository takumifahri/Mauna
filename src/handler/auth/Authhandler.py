from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union, cast
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import re
import os
from dotenv import load_dotenv

from ...database import get_db
from ...config.hash import hash_password, verify_password
from ...models.user import User, UserRole

# Load environment variables
load_dotenv()

# JWT Config from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# HTTP Bearer scheme for token verification
security = HTTPBearer()

class AuthHandler:
    """Authentication handler with JWT and active status management"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token creation failed: {str(e)}"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_current_user_from_token(self, token: str, db: Session) -> User:
        """Get user from token without security dependency"""
        payload = self.verify_token(token)
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Convert string ID to int
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token"
            )
            
        user = db.query(User).filter(User.id == user_id_int).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is still active - fix SQLAlchemy type error
        if not bool(user.is_active):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    
    def get_current_user_from_state(self, request: Request, db: Session) -> User:
        """
        Ambil user berdasarkan request.state (diisi oleh JWTAuthMiddleware).
        Digunakan sebagai dependency yang lebih ringan karena token sudah diverifikasi
        oleh middleware.
        """
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user id in token"
            )

        user = db.query(User).filter(User.id == user_id_int).first()
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

        return user

    # For OAuth2PasswordBearer
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """Get current authenticated user using OAuth2"""
        return self.get_current_user_from_token(token, db)
    
    # For HTTPBearer
    async def get_current_user_bearer(self, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
        """Get current authenticated user using Bearer token"""
        return self.get_current_user_from_token(credentials.credentials, db)
    
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
    
    async def register(self, username: str, email: str, password: str, first_name: str = None, last_name: str = None, db: Session = None) -> Dict[str, Any]:
        """Register new user"""
        if db is None:
            raise ValueError("Database session is required")
            
        try:
            # Validate email format
            if not self.validate_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            
            # Validate password strength
            password_validation = self.validate_password(password)
            if not password_validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Password validation failed", 
                        "errors": password_validation["errors"]
                    }
                )
            
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                # Cast to string to fix type error
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
            
            # Create new user
            hashed_password = hash_password(password)
            
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.USER,
                is_active=True,  # Set active by default
                is_verified=False
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(new_user.id)}
            )
            
            return {
                "success": True,
                "message": "User registered successfully",
                "access_token": access_token,
                "token_type": "bearer",
                "data": {
                    "id": new_user.id,
                    "unique_id": new_user.unique_id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "is_active": bool(new_user.is_active)
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
        """Login user with email/username and password"""
        if db is None:
            raise ValueError("Database session is required")
            
        try:
            # Find user by email or username
            user = db.query(User).filter(
                (User.email == email_or_username) | (User.username == email_or_username)
            ).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Verify password - cast to string to fix type error
            if not verify_password(password, str(user.password)):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Update user status using ORM proper approach
            setattr(user, 'is_active', True)
            setattr(user, 'last_login', datetime.utcnow())
            
            db.commit()
            db.refresh(user)
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(user.id)}
            )
            
            # Get last_login as string if exists
            last_login_str = None
            if user.last_login is not None:
                last_login_str = user.last_login.isoformat() if isinstance(user.last_login, datetime) else None
            
            return {
                "success": True,
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "data": {
                    "id": user.id,
                    "unique_id": user.unique_id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "is_active": bool(user.is_active),
                    "is_verified": bool(user.is_verified),
                    "last_login": last_login_str
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )
    
    async def logout(self, current_user: User, db: Session = None) -> Dict[str, Any]:
        """Logout user - set is_active to False"""
        if db is None:
            raise ValueError("Database session is required")
            
        try:
            # Update user status using ORM proper approach
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
            # Verify current token
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
                
            # Get user
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
                
            # Check if user is active
            if not bool(user.is_active):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
                
            # Create new token with extended expiry
            new_token = self.create_access_token(
                data={"sub": user_id},
                expires_delta=timedelta(minutes=self.access_token_expire_minutes)
            )
            
            return {
                "success": True,
                "message": "Token refreshed successfully",
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token refresh failed: {str(e)}"
            )
    
    async def get_profile(self, current_user: User) -> Dict[str, Any]:
        """Get current user profile"""
        # Safely handle datetime types
        created_at_str = None
        if current_user.created_at is not None:
            created_at_str = current_user.created_at.isoformat() if isinstance(current_user.created_at, datetime) else None
            
        updated_at_str = None
        if current_user.updated_at is not None:
            updated_at_str = current_user.updated_at.isoformat() if isinstance(current_user.updated_at, datetime) else None
            
        last_login_str = None
        if current_user.last_login is not None:
            last_login_str = current_user.last_login.isoformat() if isinstance(current_user.last_login, datetime) else None
        
        return {
            "success": True,
            "message": "Profile retrieved successfully",
            "data": {
                "id": current_user.id,
                "unique_id": current_user.unique_id,
                "username": current_user.username,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "full_name": current_user.full_name,
                "phone": current_user.phone,
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
        """Verify if user is authenticated and token is valid"""
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
    
    def require_admin(self, current_user: User):
        """Require admin role"""
        if current_user.role is not UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    def require_moderator_or_admin(self, current_user: User):
        """Require moderator or admin role"""
        # Use equality instead of `in` for Enum comparison
        if current_user.role is not UserRole.ADMIN and current_user.role is not UserRole.MODERATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Moderator or admin access required"
            )
        return current_user

# Create global auth handler instance
auth_handler = AuthHandler()

# Export commonly used functions for dependency injection
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    return await auth_handler.get_current_user(token, db)

async def get_current_user_bearer(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    return await auth_handler.get_current_user_bearer(credentials, db)

# New: dependency that uses request.state populated by middleware
async def get_current_user_from_state(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Dependency: gunakan user_id yang sudah diset di request.state oleh JWTAuthMiddleware.
    Middleware sudah memverifikasi token; disini kita hanya load user dari DB.
    """
    return auth_handler.get_current_user_from_state(request, db)

# New: role-based dependencies using state-based user
async def require_admin_state(current_user: User = Depends(get_current_user_from_state)) -> User:
    return auth_handler.require_admin(current_user)

async def require_moderator_or_admin_state(current_user: User = Depends(get_current_user_from_state)) -> User:
    return auth_handler.require_moderator_or_admin(current_user)