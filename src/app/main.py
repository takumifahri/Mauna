from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Import konfigurasi dan database
from src.config.middleware import setup_middleware
from src.database import connect_db, disconnect_db

# Import routers
from src.routes import api_router, test_router, predict_router
from src.utils.FileHandler import router as file_router
from src.routes.storageRoutes import router as storage_router

# Load environment variables
load_dotenv()

# Inisialisasi aplikasi
app = FastAPI(
    title=os.getenv("API_TITLE", "Mauna API"),
    description=os.getenv("API_DESCRIPTION", "Sign Language Learning Platform API"),
    version=os.getenv("API_VERSION", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# ✅ Get environment configuration
environment = os.getenv("ENVIRONMENT", "development")
cors_origins = os.getenv("ALLOWED_ORIGINS", "*")
cors_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
rate_limit = int(os.getenv("RATE_LIMIT", "60"))

print("\n" + "=" * 70)
print("🚀 MAUNA API - CONFIGURATION")
print("=" * 70)
print(f"📌 Environment: {environment.upper()}")
print(f"🌍 CORS Origins: {cors_origins}")
print(f"🔐 CORS Credentials: {cors_credentials}")
print(f"⚡ Rate Limit: {rate_limit} requests/minute")
print("=" * 70 + "\n")

# ✅ Setup middleware dengan environment-aware configuration
setup_middleware(
    app=app,
    rate_limit=rate_limit,
    cors_origins=cors_origins,
    cors_allow_credentials=cors_credentials,
    environment=environment
)

# Mount static files
storage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
if os.path.exists(storage_path):
    app.mount("/static", StaticFiles(directory=storage_path), name="static")
    print(f"✅ Static files mounted: {storage_path}")

# Event handlers
@app.on_event("startup")
async def startup():
    """Startup event"""
    print("\n" + "=" * 70)
    print("🚀 Starting Mauna API...")
    print("=" * 70)
    await connect_db()
    print("✅ Database connected!")
    print("=" * 70)
    print("📍 AVAILABLE ENDPOINTS:")
    print("")
    print("   🌍 PUBLIC (No authentication required):")
    print("      - GET  /                  (Root)")
    print("      - GET  /health            (Health check)")
    print("      - GET  /docs              (API documentation)")
    print("      - POST /api/auth/login    (User login)")
    print("      - POST /api/auth/register (User registration)")
    print("      - POST /predict/          (ML prediction)")
    print("      - GET  /predict/health    (Prediction health)")
    print("      - GET  /predict/classes   (Available classes)")
    print("      - GET  /storage/*         (Public files)")
    print("")
    print("   🔒 PROTECTED (Requires Bearer token):")
    print("      - GET  /api/user/profile  (User profile)")
    print("      - GET  /api/kamus         (Dictionary)")
    print("      - GET  /api/level         (Learning levels)")
    print("      - GET  /api/sublevel      (Sub-levels)")
    print("      - POST /api/user/soal/sublevel/{id}/start")
    print("      - POST /api/user/soal/sublevel/{id}/finish")
    print("      - ... (all other /api/* endpoints)")
    print("")
    print("=" * 70)
    print(f"📖 Documentation: http://localhost:8000/docs")
    print(f"🔗 ReDoc: http://localhost:8000/redoc")
    print("=" * 70 + "\n")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event"""
    await disconnect_db()
    print("\n👋 Application stopped gracefully\n")

# ✅ Register routers
# 1. PUBLIC ROUTES (No authentication)
app.include_router(test_router, tags=["Root"])
app.include_router(predict_router, tags=["ML Prediction"])
app.include_router(storage_router, tags=["Storage"])

# 2. PROTECTED ROUTES (Authentication required)
app.include_router(api_router, tags=["API"])
app.include_router(file_router, tags=["File Upload"])

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\n🚀 Starting server on {host}:{port}")
    print(f"📝 Environment: {environment}")
    print(f"🌍 CORS: {cors_origins}\n")
    
    uvicorn.run(
        "src.app.main:app",
        host=host,
        port=port,
        reload=(environment == "development")
    )