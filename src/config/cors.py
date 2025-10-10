from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os

class CORSConfig:
    """CORS configuration class"""
    
    def __init__(
        self, 
        origins: Optional[List[str]] = None,
        allow_credentials: bool = True,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None
    ):
        # ✅ Default to allow all origins in development
        environment = os.getenv("ENVIRONMENT", "development")
        
        if environment == "production" and origins:
            self.origins = origins
        else:
            # ✅ Allow all origins for development/testing
            self.origins = ["*"]
        
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["*"]  # Allow all methods
        self.allow_headers = allow_headers or ["*"]   # Allow all headers
    
    def add_to_app(self, app: FastAPI) -> FastAPI:
        """Add CORS middleware to FastAPI app"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.origins,
            allow_credentials=self.allow_credentials,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
        )
        print(f"✅ CORS middleware configured (origins: {self.origins})")
        return app
    
    def add_origin(self, origin: str):
        """Add new origin to allowed origins"""
        if self.origins != ["*"] and origin not in self.origins:
            self.origins.append(origin)
            print(f"✅ Added CORS origin: {origin}")
    
    def get_config(self) -> dict:
        """Get CORS configuration as dictionary"""
        return {
            "origins": self.origins,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allow_methods,
            "allow_headers": self.allow_headers
        }

# ✅ Create global CORS config instance - Allow all by default
cors_config = CORSConfig()

# Development CORS (more permissive)
def get_development_cors() -> CORSConfig:
    """Get development CORS configuration"""
    return CORSConfig(
        origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

# Production CORS (more restrictive)
def get_production_cors(allowed_origins: List[str]) -> CORSConfig:
    """Get production CORS configuration"""
    return CORSConfig(
        origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"]
    )