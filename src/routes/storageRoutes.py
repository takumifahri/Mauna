from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import os
from datetime import datetime
import mimetypes
from pathlib import Path

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
async def get_file(subfolder: str, filename: str, download: bool = False):
    """
    Serve uploaded files from storage - PUBLIC ACCESS
    
    Args:
        subfolder: Storage subfolder (kamus/soal)
        filename: File name
        download: Force download (default: False for viewing)
    """
    
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
    
    # Get file extension and determine media type
    file_extension = os.path.splitext(filename)[1].lower()
    
    # 🎯 Enhanced media type mapping
    media_type_map = {
        # Images
        ".png": "image/png",
        ".jpg": "image/jpeg", 
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".bmp": "image/bmp",
        ".ico": "image/x-icon",
        
        # Documents
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".txt": "text/plain",
        ".rtf": "application/rtf",
        
        # Videos
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".wmv": "video/x-ms-wmv",
        ".flv": "video/x-flv",
        ".mkv": "video/x-matroska",
        
        # Audio
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".aac": "audio/aac",
        ".flac": "audio/flac",
        
        # Archives
        ".zip": "application/zip",
        ".rar": "application/vnd.rar",
        ".7z": "application/x-7z-compressed",
        ".tar": "application/x-tar",
        ".gz": "application/gzip",
        
        # Code files
        ".json": "application/json",
        ".xml": "application/xml",
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".py": "text/x-python",
        ".java": "text/x-java",
        ".cpp": "text/x-c++",
        ".c": "text/x-c",
    }
    
    # Get media type or use mimetypes as fallback
    media_type = media_type_map.get(file_extension)
    if not media_type:
        media_type, _ = mimetypes.guess_type(filename)
        media_type = media_type or "application/octet-stream"
    
    # 🎯 Determine if file should be displayed inline or downloaded
    viewable_types = [
        "image/", "text/", "application/pdf", "application/json", 
        "application/xml", "video/", "audio/"
    ]
    
    is_viewable = any(media_type.startswith(vtype) for vtype in viewable_types)
    
    # 🔧 Set Content-Disposition header
    if download or not is_viewable:
        # Force download
        content_disposition = f'attachment; filename="{filename}"'
    else:
        # Display inline in browser
        content_disposition = f'inline; filename="{filename}"'
    
    try:
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename,
            headers={
                "Content-Disposition": content_disposition,
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "SAMEORIGIN"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

@router.get("/{subfolder}/{filename}/info")
async def get_file_info(subfolder: str, filename: str):
    """Get file information without downloading"""
    
    # Validate subfolder
    if subfolder not in STORAGE_FOLDERS:
        raise HTTPException(status_code=404, detail="Invalid subfolder")
    
    # Build file path
    file_path = os.path.join(STORAGE_FOLDERS[subfolder], filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_stat = os.stat(file_path)
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Determine media type
        media_type, _ = mimetypes.guess_type(filename)
        media_type = media_type or "application/octet-stream"
        
        return JSONResponse({
            "success": True,
            "data": {
                "filename": filename,
                "subfolder": subfolder,
                "size": file_stat.st_size,
                "size_human": _format_file_size(file_stat.st_size),
                "extension": file_extension,
                "media_type": media_type,
                "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "view_url": f"/storage/{subfolder}/{filename}",
                "download_url": f"/storage/{subfolder}/{filename}?download=true"
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")

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
                file_extension = os.path.splitext(filename)[1].lower()
                
                # Determine media type
                media_type, _ = mimetypes.guess_type(filename)
                media_type = media_type or "application/octet-stream"
                
                files.append({
                    "filename": filename,
                    "size": file_stat.st_size,
                    "size_human": _format_file_size(file_stat.st_size),
                    "extension": file_extension,
                    "media_type": media_type,
                    "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "view_url": f"/storage/{subfolder}/{filename}",
                    "download_url": f"/storage/{subfolder}/{filename}?download=true",
                    "info_url": f"/storage/{subfolder}/{filename}/info"
                })
        
        # Sort by modified time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return JSONResponse({
            "success": True,
            "subfolder": subfolder,
            "files": files,
            "count": len(files)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.get("/{subfolder}/{filename}/thumbnail")
async def get_thumbnail(subfolder: str, filename: str, size: int = 150):
    """
    Generate thumbnail for images (optional - requires Pillow)
    
    Args:
        subfolder: Storage subfolder
        filename: Image filename
        size: Thumbnail size (default: 150px)
    """
    
    # Validate subfolder
    if subfolder not in STORAGE_FOLDERS:
        raise HTTPException(status_code=404, detail="Invalid subfolder")
    
    # Build file path
    file_path = os.path.join(STORAGE_FOLDERS[subfolder], filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if it's an image
    file_extension = os.path.splitext(filename)[1].lower()
    image_extensions = [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]
    
    if file_extension not in image_extensions:
        raise HTTPException(status_code=400, detail="File is not an image")
    
    try:
        from PIL import Image
        import io
        
        # Open and resize image
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85, optimize=True)
            img_bytes.seek(0)
            
            return StreamingResponse(
                io.BytesIO(img_bytes.read()), 
                media_type="image/jpeg",
                headers={
                    "Content-Disposition": f'inline; filename="thumb_{filename}"',
                    "Cache-Control": "public, max-age=86400"  # Cache for 24 hours
                }
            )
            
    except ImportError:
        # Pillow not installed, return original image
        return FileResponse(
            path=file_path,
            media_type="image/jpeg",
            headers={"Content-Disposition": 'inline'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating thumbnail: {str(e)}")

def _format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"