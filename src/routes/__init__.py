from fastapi import APIRouter
from .auhtRoutes import router as auth_router
from .badges_routes import router as badge_router
from .userRoutes import router as user_router
from .kamusRoutes import router as kamus_router
from .level import router as level_router
from .sublevel import router as sublevel_router
from .soalRoutes import router as soal_router
from .exerciseRoutes import router as exercise_router
from .predictRoutes import router as predict_router
from .publicRoutes import public_router  # ✅ Import public router

# ✅ Buat router utama untuk /api (PROTECTED routes)
api_router = APIRouter(prefix="/api")

# Include protected routers
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
    return {
        "success": True,
        "message": "Welcome to Mauna API",
        "version": "1.0.0",
        "docs": "/docs",
        "public_endpoints": "/public/*"
    }

@test_router.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "message": "API is running"
    }

# ✅ Export routers
__all__ = [
    "api_router",
    "test_router",
    "predict_router",
    "public_router"  # ✅ Export public router
]