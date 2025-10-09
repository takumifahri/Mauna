from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from ..database.db import get_db
from ..handler.admin.Manajemen_soal import SoalHandler
from ..dto.soal_dto import (
    SoalCreateRequest, SoalUpdateRequest, SoalResponse, SoalListResponse,
    SoalDeleteResponse, SoalRestoreResponse, SoalStatisticsResponse,
    BulkDeleteSoalRequest, BulkRestoreSoalRequest
)
from ..utils.FileHandler import save_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/soal",
    tags=["Admin - Soal Management"],
    responses={
        404: {"description": "Soal not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# =====================================================================
# CREATE ENDPOINTS - Membuat soal baru
# =====================================================================

@router.post("/create", response_model=SoalResponse)
async def create_soal(
    soal_data: SoalCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create new soal (question)
    
    - **pertanyaan**: Question text (required)
    - **jawaban_benar**: Correct answer (required)
    - **sublevel_id**: SubLevel ID this question belongs to (required)
    - **dictionary_id**: Related kamus ID (optional)
    - **video_url**: Video URL for question (optional)
    """
    try:
        handler = SoalHandler(db)
        result = handler.create_soal(soal_data)
        
        status_code = 201 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error creating soal: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )
@router.post("/upload-image/{soal_id}")
async def upload_soal_image(
    soal_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """✅ Upload image for existing soal and save to database"""
    try:
        handler = SoalHandler(db)
        
        # Validate soal exists
        soal_check = handler.get_soal(soal_id)
        if not soal_check["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Soal tidak ditemukan",
                    "data": None
                },
                status_code=404
            )
        
        # Save image file
        image_path = save_image(file, "soal")
        
        if not image_path:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Gagal menyimpan gambar",
                    "data": None
                },
                status_code=500
            )
        
        # Format image URL
        image_url = f"/storage/soal/{image_path.split('/')[-1]}"
        
        # ✅ Update database dengan image_url
        result = handler.update_soal_image(soal_id, image_url)
        
        if result["success"]:
            # Add file path info to response
            result["data"]["image_path"] = image_path
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error uploading soal image: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Gagal upload gambar: {str(e)}",
                "data": None
            },
            status_code=500
        )

@router.post("/upload-video/{soal_id}")
async def upload_soal_video(
    soal_id: int,
    video_url: str = Form(..., description="Video URL (e.g., YouTube, Vimeo)"),
    db: Session = Depends(get_db)
):
    """✅ Update video URL for existing soal"""
    try:
        handler = SoalHandler(db)
        
        # Validate soal exists
        soal_check = handler.get_soal(soal_id)
        if not soal_check["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Soal tidak ditemukan",
                    "data": None
                },
                status_code=404
            )
        
        # ✅ Update database dengan video_url
        result = handler.update_soal_video(soal_id, video_url)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error updating soal video: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Gagal update video: {str(e)}",
                "data": None
            },
            status_code=500
        )

# =====================================================================
# READ ENDPOINTS - Mengambil data soal
# =====================================================================
@router.get("/list", response_model=SoalListResponse)
async def list_soal(
    search: Optional[str] = Query(None, description="Search in question or answer"),
    sublevel_id: Optional[int] = Query(None, description="Filter by sublevel ID"),
    level_id: Optional[int] = Query(None, description="Filter by level ID"),
    dictionary_id: Optional[int] = Query(None, description="Filter by dictionary ID"),
    include_deleted: bool = Query(False, description="Include soft deleted items"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    use_cache: bool = Query(True, description="Use cached data"),
    db: Session = Depends(get_db)
):
    """
    ✅ List ALL soal tanpa pagination dengan caching 3 menit
    
    **Features:**
    - No pagination - returns all data
    - 3 minutes cache (180 seconds)
    - Includes image_url & video_url from database
    
    **Filters:**
    - **search**: Search in question text or answer
    - **sublevel_id**: Filter by specific sublevel
    - **level_id**: Filter by specific level (via sublevel)
    - **dictionary_id**: Filter by related kamus
    - **include_deleted**: Include soft deleted items
    
    **Sorting:**
    - **sort_by**: Field to sort by (created_at, updated_at, question, answer)
    - **sort_order**: Sort direction (asc/desc)
    
    **Cache:**
    - **use_cache**: Enable/disable caching (default: true)
    """
    try:
        handler = SoalHandler(db)
        result = handler.list_soal(
            search=search,
            sublevel_id=sublevel_id,
            level_id=level_id,
            dictionary_id=dictionary_id,
            include_deleted=include_deleted,
            sort_by=sort_by,
            sort_order=sort_order,
            use_cache=use_cache
        )
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error listing soal: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": [],
                "total": 0,
                "filters": None,
                "cached": False
            },
            status_code=500
        )

@router.get("/{soal_id}", response_model=SoalResponse)
async def get_soal(
    soal_id: int,
    db: Session = Depends(get_db)
):
    """Get single soal by ID with detailed information"""
    try:
        handler = SoalHandler(db)
        result = handler.get_soal(soal_id)
        
        status_code = 200 if result["success"] else 404
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error getting soal {soal_id}: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )

# =====================================================================
# UPDATE ENDPOINTS - Mengupdate soal
# =====================================================================

@router.patch("/{soal_id}", response_model=SoalResponse)
async def update_soal(
    soal_id: int,
    soal_data: SoalUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update existing soal
    
    - **pertanyaan**: Question text (optional)
    - **jawaban_benar**: Correct answer (optional)  
    - **sublevel_id**: SubLevel ID (optional)
    - **dictionary_id**: Related kamus ID (optional)
    - **video_url**: Video URL (optional)
    
    Only provided fields will be updated.
    """
    try:
        handler = SoalHandler(db)
        result = handler.update_soal(soal_id, soal_data)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error updating soal {soal_id}: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )

# =====================================================================
# DELETE ENDPOINTS - Menghapus soal
# =====================================================================

@router.delete("/{soal_id}", response_model=SoalDeleteResponse)
async def delete_soal(
    soal_id: int,
    permanent: bool = Query(False, description="Permanent delete (default: soft delete)"),
    db: Session = Depends(get_db)
):
    """
    Delete soal (soft delete by default)
    
    - **permanent**: If true, permanently delete the soal
    - Default behavior is soft delete (can be restored)
    """
    try:
        handler = SoalHandler(db)
        result = handler.delete_soal(soal_id, permanent)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error deleting soal {soal_id}: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )

@router.post("/bulk-delete", response_model=SoalDeleteResponse)
async def bulk_delete_soal(
    request: BulkDeleteSoalRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk delete multiple soal
    
    - **ids**: List of soal IDs to delete
    - **permanent**: If true, permanently delete all soal
    """
    try:
        handler = SoalHandler(db)
        result = handler.bulk_delete_soal(request)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error bulk deleting soal: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )

# =====================================================================
# RESTORE ENDPOINTS - Memulihkan soal yang dihapus
# =====================================================================

@router.post("/{soal_id}/restore", response_model=SoalRestoreResponse)
async def restore_soal(
    soal_id: int,
    db: Session = Depends(get_db)
):
    """Restore soft deleted soal"""
    try:
        handler = SoalHandler(db)
        result = handler.restore_soal(soal_id)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error restoring soal {soal_id}: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )

@router.post("/bulk-restore", response_model=SoalRestoreResponse)
async def bulk_restore_soal(
    request: BulkRestoreSoalRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk restore multiple soft deleted soal
    
    - **ids**: List of soal IDs to restore
    """
    try:
        handler = SoalHandler(db)
        result = handler.bulk_restore_soal(request)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error bulk restoring soal: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )

# =====================================================================
# HELPER ENDPOINTS - Untuk dropdown dan statistik
# =====================================================================

@router.get("/helpers/available-kamus")
async def get_available_kamus(
    search: Optional[str] = Query(None, description="Search kamus"),
    db: Session = Depends(get_db)
):
    """Get available kamus for dropdown/selection"""
    try:
        handler = SoalHandler(db)
        result = handler.get_available_kamus(search)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error getting available kamus: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": []
            },
            status_code=500
        )

@router.get("/helpers/available-sublevels")
async def get_available_sublevels(
    level_id: Optional[int] = Query(None, description="Filter by level ID"),
    db: Session = Depends(get_db)
):
    """Get available sublevels for dropdown/selection"""
    try:
        handler = SoalHandler(db)
        result = handler.get_available_sublevels(level_id)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error getting available sublevels: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": []
            },
            status_code=500
        )

@router.get("/statistics", response_model=SoalStatisticsResponse)
async def get_soal_statistics(
    db: Session = Depends(get_db)
):
    """Get soal statistics for dashboard"""
    try:
        handler = SoalHandler(db)
        result = handler.get_soal_statistics()
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error getting soal statistics: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )

# =====================================================================
# ADVANCED ENDPOINTS - Untuk fitur lanjutan
# =====================================================================

@router.get("/deleted/list")
async def list_deleted_soal(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """✅ List only soft deleted soal for restore management (NO PAGINATION)"""
    try:
        handler = SoalHandler(db)
        result = handler.list_soal(
            search=search,
            include_deleted=True,
            sort_by="deleted_at",
            sort_order="desc"
        )
        
        # Filter only deleted items
        if result["success"] and result["data"]:
            deleted_only = [item for item in result["data"] if item["is_deleted"]]
            result["data"] = deleted_only
            result["total"] = len(deleted_only)
        
        status_code = 200 if result["success"] else 400
        return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error listing deleted soal: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": [],
                "total": 0,
                "filters": None
            },
            status_code=500
        )
        
@router.post("/create-with-image")
async def create_soal_with_image(
    pertanyaan: str = Form(...),
    jawaban_benar: str = Form(...),
    sublevel_id: int = Form(...),
    dictionary_id: Optional[int] = Form(None),
    video_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """✅ Create soal with optional image upload in single request"""
    try:
        # Create soal first
        soal_data = SoalCreateRequest(
            pertanyaan=pertanyaan,
            jawaban_benar=jawaban_benar,
            sublevel_id=sublevel_id,
            dictionary_id=dictionary_id,
            video_url=video_url
        )
        
        handler = SoalHandler(db)
        result = handler.create_soal(soal_data)
        
        if not result["success"]:
            return JSONResponse(content=result, status_code=400)
        
        # Upload image if provided
        if file and result["data"]:
            try:
                soal_id = result["data"]["id"]
                image_path = save_image(file, "soal")
                
                if image_path:
                    # Format image URL
                    image_url = f"/storage/soal/{image_path.split('/')[-1]}"
                    
                    # ✅ Update database dengan image_url
                    update_result = handler.update_soal_image(soal_id, image_url)
                    
                    if update_result["success"]:
                        result["data"] = update_result["data"]
                        result["message"] += " dengan gambar"
                    
            except Exception as img_error:
                logger.warning(f"Failed to upload image for soal: {img_error}")
        
        return JSONResponse(content=result, status_code=201)
        
    except Exception as e:
        logger.error(f"Error creating soal with image: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None
            },
            status_code=500
        )