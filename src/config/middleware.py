from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
import time
import re
from typing import List, Optional, Union, Dict, Any

# Load environment variables
load_dotenv()

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk JWT Authentication
    
    Middleware ini memeriksa token JWT di protected routes dan 
    memverifikasinya sebelum mengizinkan akses ke endpoint.
    
    Attributes:
        public_paths: Daftar path yang dapat diakses tanpa autentikasi
        exclude_paths: Daftar path yang dikecualikan dari middleware
    """
    
    def __init__(
        self, 
        app,
        public_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        # Path publik default jika tidak ada yang disediakan
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
        
        # Path yang sepenuhnya dikecualikan dari middleware
        self.exclude_paths = exclude_paths or [
            "/metrics",
            "/_ah/.*"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Proses setiap request melalui middleware
        
        Args:
            request: Request objek dari FastAPI
            call_next: Handler untuk memanggil middleware berikutnya
            
        Returns:
            Response dari endpoint atau error response
        """
        # Mulai pengukuran waktu untuk pelacakan performa
        start_time = time.time()
        
        # Periksa apakah path harus dikecualikan dari middleware
        if self._is_path_excluded(request.url.path):
            response = await call_next(request)
            return response
            
        # Periksa apakah path adalah publik (tidak perlu auth)
        if self._is_public_path(request.url.path):
            response = await call_next(request)
            self._add_process_time_header(response, start_time)
            return response
        
        # Untuk protected paths, verifikasi token JWT
        auth_header = request.headers.get("Authorization")
        
        # Tidak ada token yang disediakan
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": "Authorization header tidak ada atau tidak valid",
                    "error": "unauthorized",
                    "status_code": status.HTTP_401_UNAUTHORIZED
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Ekstrak token
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Verifikasi token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Periksa apakah token telah kedaluwarsa
            exp = payload.get("exp")
            if not exp or time.time() > exp:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "message": "Token telah kedaluwarsa",
                        "error": "token_expired", 
                        "status_code": status.HTTP_401_UNAUTHORIZED
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Tambahkan info user ke request state untuk digunakan handler
            request.state.user_id = payload.get("sub")
            request.state.username = payload.get("username")
            request.state.role = payload.get("role")
            request.state.jwt_payload = payload
            
            # Lanjutkan pemrosesan request
            response = await call_next(request)
            self._add_process_time_header(response, start_time)
            return response
            
        except JWTError as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "message": f"Token autentikasi tidak valid: {str(e)}",
                    "error": "invalid_token",
                    "status_code": status.HTTP_401_UNAUTHORIZED
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": f"Error autentikasi: {str(e)}",
                    "error": "server_error",
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            )
    
    def _is_public_path(self, path: str) -> bool:
        """
        Periksa apakah path ada di daftar path publik (mendukung regex)
        
        Args:
            path: Path URL yang akan diperiksa
            
        Returns:
            Boolean yang menunjukkan apakah path publik
        """
        for public_path in self.public_paths:
            # Periksa pola regex
            if public_path.endswith(".*"):
                pattern = f"^{public_path[:-2]}.*$"
                if re.match(pattern, path):
                    return True
            # Perbandingan path langsung
            elif path == public_path:
                return True
        return False
    
    def _is_path_excluded(self, path: str) -> bool:
        """
        Periksa apakah path harus dikecualikan dari middleware
        
        Args:
            path: Path URL yang akan diperiksa
            
        Returns:
            Boolean yang menunjukkan apakah path dikecualikan
        """
        for excluded_path in self.exclude_paths:
            # Periksa pola regex
            if excluded_path.endswith(".*"):
                pattern = f"^{excluded_path[:-2]}.*$"
                if re.match(pattern, path):
                    return True
            # Perbandingan path langsung
            elif path == excluded_path:
                return True
        return False
    
    def _add_process_time_header(self, response, start_time: float):
        """
        Tambahkan waktu pemrosesan ke header response
        
        Args:
            response: Response objek
            start_time: Waktu mulai pemrosesan
        """
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware untuk rate limiting
    
    Middleware ini membatasi jumlah request yang dapat dibuat klien
    dalam periode waktu tertentu untuk mencegah abuse.
    
    Attributes:
        rate_limit: Jumlah maksimum request per menit
        clients: Dictionary untuk menyimpan riwayat request client
        window_seconds: Periode waktu untuk rate limiting (detik)
        exclude_paths: Path yang dikecualikan dari rate limiting
    """
    
    def __init__(
        self, 
        app,
        rate_limit_per_minute: int = 60,
        exclude_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute
        self.clients = {}  # Menyimpan riwayat request client
        self.window_seconds = 60  # Window 1 menit
        
        # Path yang dikecualikan dari rate limiting
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/_ah/.*",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Proses setiap request melalui middleware
        
        Args:
            request: Request objek dari FastAPI
            call_next: Handler untuk memanggil middleware berikutnya
            
        Returns:
            Response dari endpoint atau error response
        """
        # Lewati rate limiting untuk excluded paths
        if self._is_path_excluded(request.url.path):
            return await call_next(request)
        
        # Dapatkan pengenal client (alamat IP atau JWT user_id jika tersedia)
        client_id = self._get_client_id(request)
        
        # Periksa apakah client telah melampaui rate limit
        current_time = time.time()
        
        if client_id in self.clients:
            # Bersihkan request lama
            self.clients[client_id] = [
                timestamp for timestamp in self.clients[client_id]
                if current_time - timestamp < self.window_seconds
            ]
            
            # Periksa apakah rate limit terlampaui
            if len(self.clients[client_id]) >= self.rate_limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "message": "Rate limit terlampaui. Silakan coba lagi nanti.",
                        "error": "rate_limit_exceeded",
                        "status_code": status.HTTP_429_TOO_MANY_REQUESTS
                    },
                    headers={"Retry-After": "60"}
                )
            
            # Tambahkan timestamp request saat ini
            self.clients[client_id].append(current_time)
        else:
            # Request pertama dari client ini
            self.clients[client_id] = [current_time]
        
        # Proses request
        response = await call_next(request)
        
        # Tambahkan header rate limit
        remaining = self.rate_limit - len(self.clients[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Dapatkan pengenal client untuk rate limiting
        
        Args:
            request: Request objek dari FastAPI
            
        Returns:
            String pengenal unik untuk client
        """
        # Jika terotentikasi, gunakan ID user dari JWT
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Gunakan IP client
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        
        if forwarded_for:
            # Ambil IP pertama jika disediakan beberapa
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _is_path_excluded(self, path: str) -> bool:
        """
        Periksa apakah path harus dikecualikan dari rate limiting
        
        Args:
            path: Path URL yang akan diperiksa
            
        Returns:
            Boolean yang menunjukkan apakah path dikecualikan
        """
        for excluded_path in self.exclude_paths:
            # Periksa pola regex
            if excluded_path.endswith(".*"):
                pattern = f"^{excluded_path[:-2]}.*$"
                if re.match(pattern, path):
                    return True
            # Perbandingan path langsung
            elif path == excluded_path:
                return True
        return False

class EnhancedCORSMiddleware(BaseHTTPMiddleware):
    """
    Middleware yang disempurnakan untuk CORS (Cross-Origin Resource Sharing)
    
    Middleware ini menangani header CORS untuk permintaan cross-origin dengan
    lebih fleksibel dan fitur tambahan dibandingkan middleware CORS bawaan.
    
    Attributes:
        allow_origins: Asal yang diizinkan (origins)
        allow_methods: Metode HTTP yang diizinkan
        allow_headers: Header yang diizinkan
        allow_credentials: Apakah kredensial diizinkan
        max_age: Berapa lama preflight response di-cache (detik)
        expose_headers: Header yang diekspos ke browser
    """
    
    def __init__(
        self, 
        app,
        allow_origins: Union[List[str], str] = ["*"],
        allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers: List[str] = ["*"],
        allow_credentials: bool = True,
        max_age: int = 600,  # 10 menit
        expose_headers: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.max_age = max_age
        self.expose_headers = expose_headers or [
            "Content-Length", 
            "Content-Type", 
            "X-Process-Time",
            "X-RateLimit-Limit", 
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Proses setiap request melalui middleware
        
        Args:
            request: Request objek dari FastAPI
            call_next: Handler untuk memanggil middleware berikutnya
            
        Returns:
            Response dengan header CORS yang sesuai
        """
        # Tangani permintaan OPTIONS preflight
        if request.method == "OPTIONS":
            return self._create_preflight_response(request)
        
        # Proses permintaan
        response = await call_next(request)
        
        # Tambahkan header CORS ke response
        origin = request.headers.get("Origin")
        
        if origin:
            # Periksa apakah origin diizinkan
            if self._is_origin_allowed(origin):
                response.headers["Access-Control-Allow-Origin"] = origin
                
                # Jika kita mengizinkan kredensial, kita harus menentukan asal
                # dan tidak dapat menggunakan wildcard "*"
                if self.allow_credentials:
                    response.headers["Access-Control-Allow-Credentials"] = "true"
                
                # Tambahkan header CORS lainnya
                response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        return response
    
    def _create_preflight_response(self, request: Request):
        """
        Buat response untuk permintaan preflight CORS
        
        Args:
            request: Request objek dari FastAPI
            
        Returns:
            JSONResponse dengan header CORS yang sesuai
        """
        origin = request.headers.get("Origin")
        
        headers = {}
        
        if origin and self._is_origin_allowed(origin):
            headers["Access-Control-Allow-Origin"] = origin
            
            if self.allow_credentials:
                headers["Access-Control-Allow-Credentials"] = "true"
            
            # Metode yang diminta
            requested_method = request.headers.get("Access-Control-Request-Method")
            if requested_method and requested_method in self.allow_methods:
                headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            
            # Header yang diminta
            requested_headers = request.headers.get("Access-Control-Request-Headers")
            if requested_headers:
                if "*" in self.allow_headers:
                    headers["Access-Control-Allow-Headers"] = requested_headers
                else:
                    headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            
            # Max age
            headers["Access-Control-Max-Age"] = str(self.max_age)
        
        return JSONResponse(content={}, headers=headers)
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """
        Periksa apakah origin diizinkan
        
        Args:
            origin: Origin yang akan diperiksa
            
        Returns:
            Boolean yang menunjukkan apakah origin diizinkan
        """
        if isinstance(self.allow_origins, str) and self.allow_origins == "*":
            return True
        
        if isinstance(self.allow_origins, list):
            if "*" in self.allow_origins:
                return True
            
            return origin in self.allow_origins
        
        return False

def setup_middleware(
    app: FastAPI, 
    jwt_public_paths: Optional[List[str]] = None,
    rate_limit: int = 60,
    cors_origins: Union[List[str], str] = ["*"],
    cors_allow_credentials: bool = True,
    environment: str = "development"
) -> FastAPI:
    """
    Fungsi bantuan untuk mengatur semua middleware dengan mudah
    
    Args:
        app: Aplikasi FastAPI
        jwt_public_paths: Path publik untuk JWT middleware
        rate_limit: Batas rate per menit
        cors_origins: Origins yang diizinkan untuk CORS
        cors_allow_credentials: Apakah kredensial diizinkan untuk CORS
        environment: Lingkungan deployment ('development' atau 'production')
        
    Returns:
        Aplikasi FastAPI dengan middleware terpasang
    """
    # Default public paths
    default_public_paths = [
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
    
    # Setup CORS berdasarkan environment
    if environment == "production":
        # Lebih ketat untuk production
        app.add_middleware(
            EnhancedCORSMiddleware,
            allow_origins=cors_origins,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Accept"],
            allow_credentials=cors_allow_credentials,
            max_age=3600  # 1 jam cache untuk production
        )
        print("✅ Production CORS middleware configured")
    else:
        # Lebih permisif untuk development
        app.add_middleware(
            EnhancedCORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
            max_age=600  # 10 menit cache untuk development
        )
        print("✅ Development CORS middleware configured")
    
    # Setup Rate Limiting
    app.add_middleware(
        RateLimitMiddleware, 
        rate_limit_per_minute=rate_limit
    )
    print(f"✅ Rate limit middleware configured ({rate_limit} requests/minute)")
    
    # Setup JWT Authentication
    app.add_middleware(
        JWTAuthMiddleware,
        public_paths=jwt_public_paths or default_public_paths
    )
    print("✅ JWT authentication middleware configured")
    
    return app