from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Union

from ..database import get_db
from ..config.middleware import require_moderator_or_admin
from ..handler.admin.manajemen_level import Level_Management
from ..dto import (
    LevelCreateRequest, LevelUpdateRequest, LevelResponse,
    LevelListResponse, LevelDeleteResponse, LevelRestoreResponse,
    LevelStatisticsResponse, LevelBulkDeleteRequest, LevelBulkRestoreRequest
)

router = APIRouter(
    prefix="/admin/levels",
    tags=["Admin - Level Management"],
    # dependencies=[Depends(require_moderator_or_admin)],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin/Moderator Only"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)

# ✅ Support both JSON and Form Data
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=LevelResponse)
async def create_level(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    level_data: Optional[LevelCreateRequest] = None,
    # Form data (optional)
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tujuan: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Create new level - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if level_data is not None:
        # JSON input
        data_dict = level_data.dict()
    elif name is not None:
        # Form data input
        data_dict = {
            "name": name,
            "description": description,
            "tujuan": tujuan
        }
        # Remove None values
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either JSON body or form data (name) is required"
        )
    
    # Validate required fields
    if not data_dict.get("name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required"
        )
    
    level_manager = Level_Management(db)
    result = level_manager.create_level(data_dict)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.put("/{level_id}", status_code=status.HTTP_200_OK, response_model=LevelResponse)
async def update_level(
    level_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    level_data: Optional[LevelUpdateRequest] = None,
    # Form data (optional)
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tujuan: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """Update level - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if level_data is not None:
        # JSON input
        data_dict = level_data.dict(exclude_unset=True)
    else:
        # Form data input
        data_dict = {}
        if name is not None:
            data_dict["name"] = name
        if description is not None:
            data_dict["description"] = description
        if tujuan is not None:
            data_dict["tujuan"] = tujuan
    
    if not data_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update"
        )
    
    level_manager = Level_Management(db)
    result = level_manager.update_level(level_id, data_dict)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

# ✅ Bulk operations with JSON support
@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_levels(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    bulk_data: Optional[LevelBulkDeleteRequest] = None,
    # Form data (optional)
    ids: Optional[str] = Form(None, description="Comma-separated level IDs"),
    permanent: Optional[bool] = Form(False, description="Permanent delete")
) -> Dict[str, Any]:
    """Bulk delete levels - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if bulk_data is not None:
        # JSON input
        level_ids = bulk_data.ids
        is_permanent = bulk_data.permanent
    elif ids is not None:
        # Form data input
        try:
            level_ids = [int(id_str.strip()) for id_str in ids.split(",") if id_str.strip()]
            is_permanent = permanent or False
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format. Use comma-separated integers."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either JSON body or form data (ids) is required"
        )
    
    if not level_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one level ID is required"
        )
    
    level_manager = Level_Management(db)
    result = level_manager.bulk_delete_levels(
        level_ids=level_ids,
        permanent=is_permanent
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/bulk-restore", status_code=status.HTTP_200_OK)
async def bulk_restore_levels(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    bulk_data: Optional[LevelBulkRestoreRequest] = None,
    # Form data (optional)
    ids: Optional[str] = Form(None, description="Comma-separated level IDs")
) -> Dict[str, Any]:
    """Bulk restore levels - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if bulk_data is not None:
        # JSON input
        level_ids = bulk_data.ids
    elif ids is not None:
        # Form data input
        try:
            level_ids = [int(id_str.strip()) for id_str in ids.split(",") if id_str.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format. Use comma-separated integers."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either JSON body or form data (ids) is required"
        )
    
    if not level_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one level ID is required"
        )
    
    level_manager = Level_Management(db)
    result = level_manager.bulk_restore_levels(level_ids=level_ids)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

# ✅ Keep existing GET routes unchanged
@router.get("/", status_code=status.HTTP_200_OK, response_model=LevelListResponse)
async def get_all_levels(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    include_deleted: bool = Query(False, description="Include soft deleted records"),
    # current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get all levels with pagination - Admin/Moderator only"""
    level_manager = Level_Management(db)
    result = level_manager.get_all_levels(
        limit=limit,
        offset=offset,
        include_deleted=include_deleted
    )
    return result

@router.get("/search", status_code=status.HTTP_200_OK, response_model=LevelListResponse)
async def search_levels(
    request: Request,
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_deleted: bool = Query(False),
    # current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Search levels by name, description, or objective - Admin/Moderator only"""
    level_manager = Level_Management(db)
    result = level_manager.search_levels(
        query=q,
        limit=limit,
        offset=offset,
        include_deleted=include_deleted
    )
    return result

@router.get("/statistics", status_code=status.HTTP_200_OK, response_model=LevelStatisticsResponse)
async def get_level_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get level statistics - Admin/Moderator only"""
    level_manager = Level_Management(db)
    result = level_manager.get_level_statistics()
    return result

@router.get("/deleted", status_code=status.HTTP_200_OK, response_model=LevelListResponse)
async def get_deleted_levels(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get all soft deleted levels - Admin/Moderator only"""
    level_manager = Level_Management(db)
    result = level_manager.get_deleted_levels(limit=limit, offset=offset)
    return result

@router.get("/{level_id}", status_code=status.HTTP_200_OK, response_model=LevelResponse)
async def get_level(
    level_id: int,
    request: Request,
    db: Session = Depends(get_db),
    include_deleted: bool = Query(False),
    # current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get level by ID - All user"""
    level_manager = Level_Management(db)
    result = level_manager.get_level(level_id, include_deleted=include_deleted)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@router.get("/{level_id}/with-sublevels", status_code=status.HTTP_200_OK)
async def get_level_with_sublevels(
    level_id: int,
    request: Request,
    db: Session = Depends(get_db),
    include_deleted: bool = Query(False),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get level with all its sublevels - Admin/Moderator only"""
    level_manager = Level_Management(db)
    result = level_manager.get_level_with_sublevels(
        level_id, 
        include_deleted=include_deleted
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@router.delete("/{level_id}", status_code=status.HTTP_200_OK, response_model=LevelDeleteResponse)
async def delete_level(
    level_id: int,
    request: Request,
    db: Session = Depends(get_db),
    permanent: bool = Query(False, description="Permanent delete instead of soft delete"),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Delete level (soft or permanent) - Admin/Moderator only"""
    level_manager = Level_Management(db)
    result = level_manager.delete_level(level_id, permanent=permanent)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/{level_id}/restore", status_code=status.HTTP_200_OK, response_model=LevelRestoreResponse)
async def restore_level(
    level_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Restore soft deleted level - Admin/Moderator only"""
    level_manager = Level_Management(db)
    result = level_manager.restore_level(level_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result