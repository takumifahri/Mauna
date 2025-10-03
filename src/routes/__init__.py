from fastapi import APIRouter
from .auhtRoutes import router as auth_router
from .badges_routes import router as badge_router
from .userRoutes import router as user_router
from .kamusRoutes import router as kamus_router
# Buat router utama untuk /api
api_router = APIRouter(prefix="/api")

# Tambahkan semua sub-router ke api_router
api_router.include_router(auth_router)
api_router.include_router(badge_router)
api_router.include_router(user_router)
api_router.include_router(kamus_router)
# Testing router untuk debugging dan health checks
test_router = APIRouter(tags=["Testing"])

@test_router.get("/")
async def root():
    """Root endpoint untuk testing"""
    return {
        "message": "SMT 5 API is running",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "healthy"
    }

@test_router.get("/test")
async def test_endpoint():
    """Test endpoint untuk memverifikasi API responsiveness"""
    return {
        "status": "success",
        "message": "Test endpoint is working properly",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Export semua router yang dibutuhkan
__all__ = ["api_router", "test_router"]