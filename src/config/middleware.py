from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import time
import re
from typing import Callable, List, Optional, Union, Dict, Any, Awaitable
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme untuk dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
security = HTTPBearer()

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk JWT Authentication
    
    Middleware ini memeriksa token JWT di protected routes dan 
    memverifikasinya sebelum mengizinkan akses ke endpoint.
    """
    
    def __init__(
        self, 
        app,
        public_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/static/.*",
            "/favicon.ico"
        ]
        
        self.exclude_paths = exclude_paths or [
            "/metrics",
            "/_ah/.*"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Proses setiap request melalui middleware"""
        start_time = time.time()
        
        # Skip excluded paths
        if self._is_path_excluded(request.url.path):
            response = await call_next(request)
            return response
            
        # Allow public paths
        if self._is_public_path(request.url.path):
            response = await call_next(request)
            self._add_process_time_header(response, start_time)
            return response
        
        # Verify JWT for protected paths
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": "Authorization header tidak ada atau tidak valid",
                    "error": "unauthorized"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token expiration
            exp = payload.get("exp")
            if not exp or time.time() > exp:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "message": "Token telah kedaluwarsa",
                        "error": "token_expired"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.username = payload.get("username")
            request.state.role = payload.get("role")
            request.state.jwt_payload = payload
            
            response = await call_next(request)
            self._add_process_time_header(response, start_time)
            return response
            
        except JWTError as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": f"Token tidak valid: {str(e)}",
                    "error": "invalid_token"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": f"Error autentikasi: {str(e)}",
                    "error": "server_error"
                }
            )
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public"""
        for public_path in self.public_paths:
            if public_path.endswith(".*"):
                pattern = f"^{public_path[:-2]}.*$"
                if re.match(pattern, path):
                    return True
            elif path == public_path:
                return True
        return False
    
    def _is_path_excluded(self, path: str) -> bool:
        """Check if path is excluded"""
        for excluded_path in self.exclude_paths:
            if excluded_path.endswith(".*"):
                pattern = f"^{excluded_path[:-2]}.*$"
                if re.match(pattern, path):
                    return True
            elif path == excluded_path:
                return True
        return False
    
    def _add_process_time_header(self, response, start_time: float):
        """Add process time header"""
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware untuk rate limiting"""
    
    def __init__(self, app, rate_limit_per_minute: int = 60, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute
        self.clients = {}
        self.window_seconds = 60
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/_ah/.*", "/favicon.ico"]
    
    async def dispatch(self, request: Request, call_next):
        """Process rate limiting"""
        if self._is_path_excluded(request.url.path):
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        if client_id in self.clients:
            self.clients[client_id] = [
                timestamp for timestamp in self.clients[client_id]
                if current_time - timestamp < self.window_seconds
            ]
            
            if len(self.clients[client_id]) >= self.rate_limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "message": "Rate limit terlampaui",
                        "error": "rate_limit_exceeded"
                    },
                    headers={"Retry-After": "60"}
                )
            
            self.clients[client_id].append(current_time)
        else:
            self.clients[client_id] = [current_time]
        
        response = await call_next(request)
        
        remaining = self.rate_limit - len(self.clients[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier"""
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _is_path_excluded(self, path: str) -> bool:
        """Check if path is excluded from rate limiting"""
        for excluded_path in self.exclude_paths:
            if excluded_path.endswith(".*"):
                pattern = f"^{excluded_path[:-2]}.*$"
                if re.match(pattern, path):
                    return True
            elif path == excluded_path:
                return True
        return False

class EnhancedCORSMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware"""
    
    def __init__(
        self, 
        app,
        allow_origins: Union[List[str], str] = ["*"],
        allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers: List[str] = ["*"],
        allow_credentials: bool = True,
        max_age: int = 600,
        expose_headers: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.max_age = max_age
        self.expose_headers = expose_headers or [
            "Content-Length", "Content-Type", "X-Process-Time",
            "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process CORS"""
        if request.method == "OPTIONS":
            return self._create_preflight_response(request)
        
        response = await call_next(request)
        origin = request.headers.get("Origin")
        
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        return response
    
    def _create_preflight_response(self, request: Request):
        """Create preflight CORS response"""
        origin = request.headers.get("Origin")
        headers = {}
        
        if origin and self._is_origin_allowed(origin):
            headers["Access-Control-Allow-Origin"] = origin
            
            if self.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"
            
            requested_method = request.headers.get("Access-Control-Request-Method")
            if requested_method and requested_method in self.allow_methods:
                headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            
            requested_headers = request.headers.get("Access-Control-Request-Headers")
            if requested_headers:
                if "*" in self.allow_headers:
                    headers["Access-Control-Allow-Headers"] = requested_headers
                else:
                    headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            
            headers["Access-Control-Max-Age"] = str(self.max_age)
        
        return JSONResponse(content={}, headers=headers)
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if isinstance(self.allow_origins, str) and self.allow_origins == "*":
            return True
        
        if isinstance(self.allow_origins, list):
            if "*" in self.allow_origins:
                return True
            return origin in self.allow_origins
        
        return False

# =============================================================================
# AUTH HANDLER & DEPENDENCIES - CENTRALIZED HERE
# =============================================================================

class AuthManager:
    """Centralized authentication and authorization manager"""
    
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
    
    def get_current_user_from_state(self, request: Request, db: Session) -> Any:
        """Get user from request state (set by middleware)"""
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

        # Import here to avoid circular imports
        from ..models.user import User
        
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

# Global auth manager instance
auth_manager = AuthManager()

# =============================================================================
# CLEAN DEPENDENCIES FOR ROUTES - FIXED
# =============================================================================

def get_current_user(request: Request, db: Session = Depends(lambda: None)) -> Any:
    """
    Clean dependency untuk mendapatkan current user
    Menggunakan request.state yang sudah diset oleh middleware
    """
    # Import database dependency inside function to avoid circular imports
    from ..database import get_db
    
    # Get fresh db session if not provided
    if db is None:
        db_gen = get_db()
        db = next(db_gen)
    
    return auth_manager.get_current_user_from_state(request, db)

def require_admin(request: Request, db: Session = Depends(lambda: None)) -> Any:
    """Clean dependency untuk require admin role"""
    # Import database dependency inside function
    from ..database import get_db
    
    # Get fresh db session if not provided
    if db is None:
        db_gen = get_db()
        db = next(db_gen)
    
    user = auth_manager.get_current_user_from_state(request, db)
    
    # Import here to avoid circular imports
    from ..models.user import UserRole
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

def require_moderator_or_admin(request: Request, db: Session = Depends(lambda: None)) -> Any:
    """Clean dependency untuk require moderator atau admin role"""
    # Import database dependency inside function
    from ..database import get_db
    
    # Get fresh db session if not provided
    if db is None:
        db_gen = get_db()
        db = next(db_gen)
    
    user = auth_manager.get_current_user_from_state(request, db)
    
    # Import here to avoid circular imports
    from ..models.user import UserRole
    
    if user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator or admin access required"
        )
    return user

def require_user_or_above(request: Request, db: Session = Depends(lambda: None)) -> Any:
    """Clean dependency untuk require minimal user role (semua role)"""
    # Import database dependency inside function
    from ..database import get_db
    
    # Get fresh db session if not provided
    if db is None:
        db_gen = get_db()
        db = next(db_gen)
    
    return auth_manager.get_current_user_from_state(request, db)

# =============================================================================
# SETUP FUNCTION
# =============================================================================

def setup_middleware(
    app: FastAPI, 
    jwt_public_paths: Optional[List[str]] = None,
    rate_limit: int = 60,
    cors_origins: Union[List[str], str] = ["*"],
    cors_allow_credentials: bool = True,
    environment: str = "development"
) -> FastAPI:
    """Setup all middleware easily"""
    
    default_public_paths = [
        "/", "/docs", "/redoc", "/openapi.json", "/health",
        "/api/auth/login", "/api/auth/register", "/api/auth/refresh",
        "/static/.*", "/favicon.ico"
    ]
    
    # Setup CORS
    if environment == "production":
        app.add_middleware(
            EnhancedCORSMiddleware,
            allow_origins=cors_origins,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Accept"],
            allow_credentials=cors_allow_credentials,
            max_age=3600
        )
        print("✅ Production CORS middleware configured")
    else:
        app.add_middleware(
            EnhancedCORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
            max_age=600
        )
        print("✅ Development CORS middleware configured")
    
    # Setup Rate Limiting
    app.add_middleware(RateLimitMiddleware, rate_limit_per_minute=rate_limit)
    print(f"✅ Rate limit middleware configured ({rate_limit} requests/minute)")
    
    # Setup JWT Authentication
    app.add_middleware(
        JWTAuthMiddleware,
        public_paths=jwt_public_paths or default_public_paths
    )
    print("✅ JWT authentication middleware configured")
    
    return app

# Export semua yang dibutuhkan
__all__ = [
    "JWTAuthMiddleware",
    "RateLimitMiddleware", 
    "EnhancedCORSMiddleware",
    "AuthManager",
    "auth_manager",
    "get_current_user",
    "require_admin", 
    "require_moderator_or_admin",
    "require_user_or_above",
    "setup_middleware"
]