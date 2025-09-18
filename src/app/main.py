from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from passlib.context import CryptContext
from dotenv import load_dotenv

# Import konfigurasi dan database
from src.config.middleware import setup_middleware
from src.database import connect_db, disconnect_db, get_db

# Import router dari modul routes
from src.routes import api_router, test_router

# Load environment variables
load_dotenv()

# Inisialisasi aplikasi
app = FastAPI(
    title="SMT 5 API",
    description="SMT 5 FastAPI Application",
    version="1.0.0"
)

# Setup middleware
environment = os.getenv("ENVIRONMENT", "development")
setup_middleware(
    app=app,
    rate_limit=int(os.getenv("RATE_LIMIT", "60")),
    cors_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    environment=environment
)

# Konfigurasi keamanan
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")  # Sesuaikan dengan prefix

# Event handler
@app.on_event("startup")
async def startup():
    """Startup event"""
    print("🚀 Starting SMT 5 API...")
    await connect_db()
    print("✅ Application ready!")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event"""
    await disconnect_db()
    print("👋 Application stopped")

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connection test"""
    try:
        # Test database query
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Tambahkan router ke aplikasi
app.include_router(test_router)  # Root router (/)
app.include_router(api_router)   # API router (/api/...)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True
    )