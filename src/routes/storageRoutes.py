from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
from datetime import datetime

# Import dari FileHandler
from ..utils.FileHandler import STORAGE_FOLDERS

router = APIRouter(
    prefix="/storage",
    tags=["Storage - Public"],
    responses={
        404: {"description": "File not found"},
    },
)

@router.get("/{subfolder}/{filename}")
async def get_file(subfolder: str, filename: str):
    """Serve uploaded files from storage - PUBLIC ACCESS"""
    
    # Validate subfolder
    if subfolder not in STORAGE_FOLDERS:
        raise HTTPException(status_code=404, detail="Invalid subfolder")
    
    # Build file path
    file_path = os.path.join(STORAGE_FOLDERS[subfolder], filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if it's actually a file (not directory)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Path is not a file")
    
    # Get file extension to determine media type
    file_extension = os.path.splitext(filename)[1].lower()
    media_type_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg", 
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }
    
    media_type = media_type_map.get(file_extension, "application/octet-stream")
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )

@router.get("/{subfolder}")
async def list_files(subfolder: str):
    """List all files in a storage subfolder - PUBLIC ACCESS"""
    
    # Validate subfolder
    if subfolder not in STORAGE_FOLDERS:
        raise HTTPException(status_code=404, detail="Invalid subfolder")
    
    storage_dir = STORAGE_FOLDERS[subfolder]
    
    # Check if directory exists
    if not os.path.exists(storage_dir):
        return JSONResponse({
            "success": True,
            "subfolder": subfolder,
            "files": [],
            "count": 0
        })
    
    try:
        # Get all files in directory
        files = []
        for filename in os.listdir(storage_dir):
            file_path = os.path.join(storage_dir, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": file_stat.st_size,
                    "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "url": f"/storage/{subfolder}/{filename}"
                })
        
        return JSONResponse({
            "success": True,
            "subfolder": subfolder,
            "files": files,
            "count": len(files)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")