# src/app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from src.config.middleware import JWTAuthMiddleware, RateLimitMiddleware
from src.database import connect_db, disconnect_db

# ✅ Import routers yang sudah kamu definisikan
from src.routes import api_router, test_router, public_router
from src.routes.predictRoutes import router as predict_router, load_model_safe # ✅ Ubah import ini
from src.utils.FileHandler import router as file_router
from src.routes.storageRoutes import router as storage_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("API_TITLE", "Mauna API"),
    description=os.getenv("API_DESCRIPTION", "Sign Language Learning Platform API"),
    version=os.getenv("API_VERSION", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# ... (Kode CORS, RateLimit, JWT middleware tetap sama) ...
environment = os.getenv("ENVIRONMENT", "development")
cors_origins = os.getenv("ALLOWED_ORIGINS", "*")
rate_limit = int(os.getenv("RATE_LIMIT", "60"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

app.add_middleware(RateLimitMiddleware, rate_limit_per_minute=rate_limit)

custom_public_paths = [
    "/", "/docs", "/redoc", "/openapi.json", "/health",
    "/api/auth/login", "/api/auth/register", "/api/auth/refresh",
    "/public", "/public/.*", "/predict", "/predict/.*",
    "/storage", "/storage/.*", "/static", "/static/.*", "/favicon.ico"
]

app.add_middleware(
    JWTAuthMiddleware,
    public_paths=custom_public_paths
)
print("✅ JWT authentication configured")

# ... (Mount static files tetap sama) ...
storage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage"))
if os.path.exists(storage_path):
    app.mount("/static", StaticFiles(directory=storage_path), name="static")
    print(f"✅ Static files mounted: {storage_path}")

# Event handlers
@app.on_event("startup")
async def startup():
    print("\n" + "=" * 70)
    print("🚀 Starting Mauna API...")
    print("=" * 70)
    await connect_db()
    print("✅ Database connected!")
    print("\n" + "=" * 70)
    print("🧠 LOADING MACHINE LEARNING MODEL...")
    # ✅ Panggil fungsi load_model_safe saat startup
    # Fungsi ini akan mencetak log detail jika ada error
    load_model_safe()
    print("=" * 70 + "\n")
    print("📍 AVAILABLE ENDPOINTS:")
    print("")
    print("   🌍 PUBLIC (No authentication required):")
    print("      - GET  /                           (Root)")
    print("      - GET  /health                     (Health check)")
    print("      - GET  /docs                       (API documentation)")
    print("      - POST /api/auth/login             (User login)")
    print("      - POST /api/auth/register          (User registration)")
    print("      - POST /predict/                   (ML prediction)")
    print("      - GET  /predict/*                  (Prediction endpoints)")
    print("      - GET  /storage/*                  (Public files)")
    print("")
    print("   ✅ PUBLIC READ-ONLY:")
    print("      - GET  /public/badges              (All badges)")
    print("      - GET  /public/badges/{id}         (Badge detail)")
    print("      - GET  /public/kamus               (All kamus)")
    print("      - GET  /public/kamus/{id}          (Kamus detail)")
    print("      - GET  /public/kamus/statistics    (Kamus stats)")
    print("      - GET  /public/levels              (All levels)")
    print("      - GET  /public/levels/{id}         (Level detail)")
    print("      - GET  /public/levels/{id}/with-sublevels")
    print("      - GET  /public/levels/statistics")
    print("      - GET  /public/sublevels           (All sublevels)")
    print("      - GET  /public/sublevels/{id}      (Sublevel detail)")
    print("      - GET  /public/sublevels/by-level/{id}")
    print("      - GET  /public/sublevels/statistics")
    print("      - GET  /public/soal/statistics")
    print("      - GET  /public/soal/helpers/available-kamus")
    print("      - GET  /public/soal/helpers/available-sublevels")
    print("")
    print("   🔒 PROTECTED (Requires Bearer token):")
    print("      - GET  /api/auth/profile           (User profile)")
    print("      - POST /api/auth/logout            (User logout)")
    print("      - POST /api/admin/kamus            (Create kamus - Admin)")
    print("      - POST /api/admin/levels           (Create level - Admin)")
    print("      - POST /api/admin/sublevels        (Create sublevel - Admin)")
    print("      - POST /api/admin/soal/create      (Create soal - Admin)")
    print("      - POST /api/user/soal/sublevel/{id}/start")
    print("      - POST /api/user/soal/sublevel/{id}/finish")
    print("      - ... (all other /api/* endpoints)")
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

# ✅ Register routers IN ORDER
app.include_router(test_router, tags=["Root"])
app.include_router(public_router, tags=["Public"])
app.include_router(predict_router, tags=["ML Prediction"]) # ✅ Menggunakan router yang baru
app.include_router(storage_router, tags=["Storage"])
app.include_router(api_router, tags=["API - Protected"])
app.include_router(file_router, tags=["File Upload"])

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\n🚀 Starting server on {host}:{port}")
    print(f"📝 Environment: {environment}")
    print(f"🌍 CORS: Allow all origins (*)\n")
    
    uvicorn.run(
        "src.app.main:app",
        host=host,
        port=port,
        reload=(environment == "development")
    )