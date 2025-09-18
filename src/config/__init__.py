"""
Configuration package for SMT 5 application.

This package contains:
- Database configuration and connection management
- JWT configuration
- CORS configuration
- Password hashing utilities
- Database seeding
"""


# CORS exports
from .cors import (
    CORSConfig,
    cors_config,
    get_development_cors,
    get_production_cors
)


# Password hash exports
from .hash import (  # Ubah dari .hash ke .password_hash
    PasswordManager,
    password_manager,
    hash_password,
    verify_password
)

from .middleware import (
    JWTAuthMiddleware,
    RateLimitMiddleware,
    EnhancedCORSMiddleware
)
__all__ = [
    
    # CORS
    'CORSConfig',
    'cors_config',
    'get_development_cors',
    'get_production_cors',
  
    # Password Hash
    'PasswordManager',
    'password_manager',
    'hash_password',
    'verify_password',
    
    # Middleware
    'JWTAuthMiddleware',
    'RateLimitMiddleware',
    'EnhancedCORSMiddleware'
    
]