from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from passlib.context import CryptContext
from dotenv import load_dotenv

# Import konfigurasi dan database
from src.config.middleware import setup_middleware
from src.database import connect_db, disconnect_db, get_db

# Import router dari modul routes
from src.routes import api_router, test_router
from src.utils.FileHandler import router as file_router
from src.routes.storageRoutes import router as storage_router
from src.routes.predictRoutes import router as predict_router  # ✅ Public router

# Load environment variables
load_dotenv()

# Inisialisasi aplikasi
app = FastAPI(
    title="Mauna API - Sign Language Learning Platform",
    description="API for Mauna Sign Language Learning Application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
environment = os.getenv("ENVIRONMENT", "development")
setup_middleware(
    app=app,
    rate_limit=int(os.getenv("RATE_LIMIT", "60")),
    cors_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    environment=environment
)

# Mount static files untuk storage
storage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
if os.path.exists(storage_path):
    app.mount("/static", StaticFiles(directory=storage_path), name="static")

# Konfigurasi keamanan
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Event handler
@app.on_event("startup")
async def startup():
    """Startup event"""
    print("=" * 60)
    print("🚀 Starting Mauna API...")
    print("=" * 60)
    await connect_db()
    print("✅ Database connected!")
    print("✅ Application ready!")
    print("=" * 60)
    print(f"📖 Docs: http://localhost:8000/docs")
    print(f"🔒 Protected API: http://localhost:8000/api/...")
    print(f"🌍 Public API: http://localhost:8000/predict/...")
    print(f"📦 Storage: http://localhost:8000/storage/...")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event"""
    await disconnect_db()
    print("👋 Application stopped")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Mauna API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/api/auth",
            "predict": "/predict (PUBLIC)",
            "storage": "/storage (PUBLIC)"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connection test"""
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "ml_model": "ready",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# ✅ Tambahkan router ke aplikasi
# PUBLIC ROUTES (No authentication required)
app.include_router(test_router, tags=["Test"])           # Root router (/)
app.include_router(predict_router, tags=["ML Prediction"])  # ✅ PUBLIC - /predict
app.include_router(storage_router, tags=["Storage"])     # ✅ PUBLIC - /storage

# PROTECTED ROUTES (Authentication required)
app.include_router(api_router, tags=["API"])             # /api/... (protected)
app.include_router(file_router, tags=["File Upload"])    # /file/... (protected)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )