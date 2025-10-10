import os
import uuid
from datetime import datetime
from fastapi import Form, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_STORAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))

STORAGE_FOLDERS = {
    "soal": os.path.join(BASE_STORAGE_PATH, "soal"),
    "kamus": os.path.join(BASE_STORAGE_PATH, "kamus"),
    "avatars": os.path.join(BASE_STORAGE_PATH, "avatars"),  # ✅ Add avatars
}

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

def ensure_storage_dirs():
    """Ensure storage directories exist with proper error handling"""
    for name, folder in STORAGE_FOLDERS.items():
        try:
            Path(folder).mkdir(parents=True, exist_ok=True)
            # Test write permission
            test_file = Path(folder) / '.write_test'
            test_file.touch()
            test_file.unlink()
            logger.info(f"✅ Storage directory ready: {folder}")
        except PermissionError as e:
            logger.warning(f"⚠️ Permission denied for {folder}: {e}")
            # Try alternative location
            alt_folder = f"/tmp/mauna_storage/{name}"
            try:
                Path(alt_folder).mkdir(parents=True, exist_ok=True)
                STORAGE_FOLDERS[name] = alt_folder
                logger.info(f"✅ Using alternative storage: {alt_folder}")
            except Exception as alt_e:
                logger.error(f"❌ Failed to create alternative storage: {alt_e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error creating {folder}: {e}")

def _ensure_dir_exists(directory: str):
    """Ensure specific directory exists when needed"""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Test write permission
        test_file = Path(directory) / '.write_test'
        test_file.touch()
        test_file.unlink()
        
        return True
    except PermissionError as e:
        logger.warning(f"Permission denied creating directory: {directory}")
        
        # Try alternative location
        alt_dir = f"/tmp/mauna_storage/{Path(directory).name}"
        try:
            Path(alt_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Using alternative directory: {alt_dir}")
            return alt_dir
        except Exception:
            return False
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename untuk menghindari karakter yang tidak diizinkan"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_')
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    filename = re.sub(r'_{2,}', '_', filename)
    return filename

def save_image(file: UploadFile, subfolder: str) -> str:
    """Save uploaded image to storage and return relative path"""
    logger.info(f"🔍 Debug: File received - filename: {file.filename}, content_type: {file.content_type}")
    
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
    
    # Ensure directory exists - with fallback handling
    dir_result = _ensure_dir_exists(storage_dir)
    if dir_result is False:
        raise HTTPException(status_code=500, detail=f"Cannot create storage directory: {storage_dir}")
    elif isinstance(dir_result, str):
        # Alternative directory was used
        storage_dir = dir_result
    
    # Generate filename
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1].lower()
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    clean_filename = sanitize_filename(filename_without_ext)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{clean_filename}_{timestamp}{file_extension}"
    
    if not file_extension:
        extension_map = {
            "image/png": ".png",
            "image/jpeg": ".jpg", 
            "image/jpg": ".jpg",
            "image/webp": ".webp"
        }
        file_extension = extension_map.get(file.content_type, ".jpg")
        unique_filename = f"{clean_filename}_{timestamp}{file_extension}"
    
    file_path = os.path.join(storage_dir, unique_filename)
    
    # Handle duplicate filenames
    counter = 1
    original_unique_filename = unique_filename
    while os.path.exists(file_path):
        filename_parts = os.path.splitext(original_unique_filename)
        unique_filename = f"{filename_parts[0]}_{counter}{filename_parts[1]}"
        file_path = os.path.join(storage_dir, unique_filename)
        counter += 1
    
    try:
        # Reset file pointer
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
        
        # Verify file was created
        if not os.path.exists(file_path):
            logger.error(f"❌ File was not created: {file_path}")
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        # Return relative path
        relative_path = f"storage/{subfolder}/{unique_filename}"
        logger.info(f"🎯 Returning relative path: {relative_path}")
        return relative_path
        
    except PermissionError as e:
        logger.error(f"❌ Permission error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Permission denied: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error saving file: {str(e)}")
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

@router.post("/upload/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    """Upload user avatar"""
    try:
        rel_path = save_image(file, "avatars")
        return JSONResponse({
            "success": True, 
            "path": rel_path,
            "url": f"/{rel_path}",
            "message": "Avatar uploaded successfully"
        })
    except HTTPException as e:
        return JSONResponse({
            "success": False, 
            "error": e.detail
        }, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Unexpected error in upload_avatar: {e}")
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