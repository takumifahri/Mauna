from fastapi import APIRouter
from .auhtRoutes import router as auth_router
from .badges_routes import router as badge_router
from .userRoutes import router as user_router
from .kamusRoutes import router as kamus_router
from .level import router as level_router
from .sublevel import router as sublevel_router
from .soalRoutes import router as soal_router
from .exerciseRoutes import router as exercise_router
from .predictRoutes import router as predict_router  # ✅ Import predict router

# ✅ Buat router utama untuk /api (PROTECTED routes)
api_router = APIRouter(prefix="/api")

# ✅ JANGAN include predict_router di sini (akan di-include langsung di main.py)
api_router.include_router(auth_router)
api_router.include_router(badge_router)
api_router.include_router(user_router)
api_router.include_router(kamus_router)
api_router.include_router(level_router)
api_router.include_router(sublevel_router)
api_router.include_router(soal_router)
api_router.include_router(exercise_router)

# ✅ Testing router
test_router = APIRouter(tags=["Testing"])

@test_router.get("/")
async def root():
    """Root endpoint untuk testing"""
    return {
        "message": "Mauna API is running",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "public_predict": "/predict/*",
            "protected_api": "/api/*"
        }
    }

@test_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Mauna API",
        "version": "1.0.0"
    }

# ✅ Export routers
__all__ = [
    "api_router",      # Protected routes (/api/*)
    "test_router",     # Test routes (/)
    "predict_router"   # ✅ Export predict_router untuk di-include di main.py
]