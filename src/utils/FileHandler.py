import os
import uuid
from datetime import datetime
from fastapi import Form, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_STORAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
STORAGE_FOLDERS = {
    "soal": os.path.join(BASE_STORAGE_PATH, "soal"),
    "kamus": os.path.join(BASE_STORAGE_PATH, "kamus"),
}
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

def ensure_storage_dirs():
    """Ensure storage directories exist with proper error handling"""
    for name, folder in STORAGE_FOLDERS.items():
        try:
            os.makedirs(folder, exist_ok=True)
            logger.info(f"✅ Storage directory created/verified: {folder}")
        except PermissionError as e:
            logger.warning(f"⚠️ Permission denied creating {folder}: {e}")
            # Don't fail the entire application startup
            continue
        except Exception as e:
            logger.error(f"❌ Unexpected error creating {folder}: {e}")
            continue

# Only call during actual file operations, not on import
def _ensure_dir_exists(directory: str):
    """Ensure specific directory exists when needed"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except PermissionError:
        logger.warning(f"Permission denied creating directory: {directory}")
        return False
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename untuk menghindari karakter yang tidak diizinkan"""
    # Hapus karakter yang tidak diizinkan untuk nama file
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Ganti spasi dengan underscore
    filename = filename.replace(' ', '_')
    # Hapus karakter non-ASCII dan ganti dengan underscore
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    # Hapus multiple underscore berturut-turut
    filename = re.sub(r'_{2,}', '_', filename)
    return filename

def save_image(file: UploadFile, subfolder: str) -> str:
    """Save uploaded image to storage and return relative path"""
    logger.info(f"🔍 Debug: File received - filename: {file.filename}, content_type: {file.content_type}")
    
    # Validasi file
    if not file or not file.filename:
        logger.error("❌ No file provided or filename is empty")
        return ""
    
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        logger.error(f"❌ Invalid content type: {file.content_type}")
        raise HTTPException(status_code=400, detail=f"File must be an image. Allowed types: {ALLOWED_IMAGE_TYPES}")
    
    # Get storage directory
    storage_dir = STORAGE_FOLDERS.get(subfolder)
    if not storage_dir:
        raise HTTPException(status_code=400, detail="Invalid storage subfolder")
    
    # Ensure directory exists when needed (not on import)
    if not _ensure_dir_exists(storage_dir):
        raise HTTPException(status_code=500, detail=f"Cannot create storage directory: {storage_dir}")
    
    # Generate filename dengan nama asli + timestamp
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1].lower()
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    # Sanitize nama file
    clean_filename = sanitize_filename(filename_without_ext)
    
    # Tambahkan timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Format: namafile_asli_YYYYMMDD_HHMMSS.ext
    unique_filename = f"{clean_filename}_{timestamp}{file_extension}"
    
    # Pastikan extension ada
    if not file_extension:
        # Fallback extension based on content type
        extension_map = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/webp": ".webp"
        }
        file_extension = extension_map.get(file.content_type, ".jpg")
        unique_filename = f"{clean_filename}_{timestamp}{file_extension}"
    
    file_path = os.path.join(storage_dir, unique_filename)
    
    # Check jika file sudah ada (kemungkinan kecil tapi bisa terjadi)
    counter = 1
    original_unique_filename = unique_filename
    while os.path.exists(file_path):
        filename_parts = os.path.splitext(original_unique_filename)
        unique_filename = f"{filename_parts[0]}_{counter}{filename_parts[1]}"
        file_path = os.path.join(storage_dir, unique_filename)
        counter += 1
    
    try:
        # Reset file pointer to beginning
        file.file.seek(0)
        
        # Read and save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            if not content:
                logger.error("❌ File content is empty")
                raise HTTPException(status_code=400, detail="File content is empty")
            
            buffer.write(content)
            logger.info(f"✅ File saved successfully: {file_path}")
            logger.info(f"📁 File size: {len(content)} bytes")
            logger.info(f"📝 Original filename: {original_filename}")
            logger.info(f"🆕 New filename: {unique_filename}")
        
        # Verify file was actually created
        if not os.path.exists(file_path):
            logger.error(f"❌ File was not created: {file_path}")
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        # Return relative path
        relative_path = f"storage/{subfolder}/{unique_filename}"
        logger.info(f"🎯 Returning relative path: {relative_path}")
        return relative_path
        
    except Exception as e:
        logger.error(f"❌ Error saving file: {str(e)}")
        # Clean up if file was partially created
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

# Initialize router
router = APIRouter(prefix="/file", tags=["File Upload"])

@router.post("/upload/soal-image")
async def upload_soal_image(file: UploadFile = File(...)):
    """Upload image for soal"""
    try:
        rel_path = save_image(file, "soal")
        return JSONResponse({
            "success": True, 
            "path": rel_path,
            "message": "Image uploaded successfully"
        })
    except HTTPException as e:
        return JSONResponse({
            "success": False, 
            "error": e.detail
        }, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Unexpected error in upload_soal_image: {e}")
        return JSONResponse({
            "success": False, 
            "error": "Internal server error"
        }, status_code=500)

@router.post("/upload/kamus-image")
async def upload_kamus_image(
    word_text: str = Form(...),
    definition: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload image for kamus entry"""
    try:
        rel_path = save_image(file, "kamus")
        return JSONResponse({
            "success": True, 
            "path": rel_path, 
            "word_text": word_text, 
            "definition": definition,
            "message": "Kamus image uploaded successfully"
        })
    except HTTPException as e:
        return JSONResponse({
            "success": False, 
            "error": e.detail
        }, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Unexpected error in upload_kamus_image: {e}")
        return JSONResponse({
            "success": False, 
            "error": "Internal server error"
        }, status_code=500)

@router.get("/init-storage")
async def initialize_storage():
    """Manual endpoint to initialize storage directories"""
    try:
        ensure_storage_dirs()
        return JSONResponse({
            "success": True,
            "message": "Storage directories initialized",
            "directories": list(STORAGE_FOLDERS.keys())
        })
    except Exception as e:
        logger.error(f"Error initializing storage: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)
