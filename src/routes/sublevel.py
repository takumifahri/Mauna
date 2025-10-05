from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Form
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from ..database import get_db
from ..config.middleware import require_moderator_or_admin
from ..handler.admin.manajemen_sublevel import SubLevel_Management
from ..dto import (
    SubLevelCreateRequest, SubLevelUpdateRequest, SubLevelResponse,
    SubLevelListResponse, SubLevelDeleteResponse, SubLevelRestoreResponse,
    SubLevelStatisticsResponse, SubLevelBulkDeleteRequest, SubLevelBulkRestoreRequest
)

router = APIRouter(
    prefix="/admin/sublevels",
    tags=["Admin - SubLevel Management"],
    dependencies=[Depends(require_moderator_or_admin)],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin/Moderator Only"},
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"},
    },
)

# ✅ Support both JSON and Form Data
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SubLevelResponse)
async def create_sublevel(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    sublevel_data: Optional[SubLevelCreateRequest] = None,
    # Form data (optional)
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tujuan: Optional[str] = Form(None),
    level_id: Optional[int] = Form(None)
) -> Dict[str, Any]:
    """Create new sublevel - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if sublevel_data is not None:
        # JSON input
        data_dict = sublevel_data.dict()
    elif name is not None and level_id is not None:
        # Form data input
        data_dict = {
            "name": name,
            "description": description,
            "tujuan": tujuan,
            "level_id": level_id
        }
        # Remove None values
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either JSON body or form data (name and level_id) is required"
        )
    
    # Validate required fields
    if not data_dict.get("name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required"
        )
    
    if not data_dict.get("level_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level ID is required"
        )
    
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.create_sublevel(data_dict)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.put("/{sublevel_id}", status_code=status.HTTP_200_OK, response_model=SubLevelResponse)
async def update_sublevel(
    sublevel_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    sublevel_data: Optional[SubLevelUpdateRequest] = None,
    # Form data (optional)
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tujuan: Optional[str] = Form(None),
    level_id: Optional[int] = Form(None)
) -> Dict[str, Any]:
    """Update sublevel - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if sublevel_data is not None:
        # JSON input
        data_dict = sublevel_data.dict(exclude_unset=True)
    else:
        # Form data input
        data_dict = {}
        if name is not None:
            data_dict["name"] = name
        if description is not None:
            data_dict["description"] = description
        if tujuan is not None:
            data_dict["tujuan"] = tujuan
        if level_id is not None:
            data_dict["level_id"] = level_id
    
    if not data_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update"
        )
    
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.update_sublevel(sublevel_id, data_dict)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

# ✅ Keep all existing GET routes unchanged (they work fine with query params)
# ... (semua GET routes tetap sama seperti sebelumnya)

@router.get("/", status_code=status.HTTP_200_OK, response_model=SubLevelListResponse)
async def get_all_sublevels(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    include_deleted: bool = Query(False, description="Include soft deleted records"),
    level_id: Optional[int] = Query(None, description="Filter by level ID"),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get all sublevels with pagination - Admin/Moderator only"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_all_sublevels(
        limit=limit,
        offset=offset,
        include_deleted=include_deleted,
        level_id=level_id
    )
    return result

@router.get("/search", status_code=status.HTTP_200_OK, response_model=SubLevelListResponse)
async def search_sublevels(
    request: Request,
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_deleted: bool = Query(False),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Search sublevels by name, description, or objective - Admin/Moderator only"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.search_sublevels(
        query=q,
        limit=limit,
        offset=offset,
        include_deleted=include_deleted
    )
    return result

@router.get("/statistics", status_code=status.HTTP_200_OK, response_model=SubLevelStatisticsResponse)
async def get_sublevel_statistics(
    request: Request,
    db: Session = Depends(get_db),
    level_id: Optional[int] = Query(None, description="Filter statistics by level ID"),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get sublevel statistics - Admin/Moderator only"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_sublevel_statistics(level_id=level_id)
    return result

@router.get("/deleted", status_code=status.HTTP_200_OK, response_model=SubLevelListResponse)
async def get_deleted_sublevels(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get all soft deleted sublevels - Admin/Moderator only"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_deleted_sublevels(limit=limit, offset=offset)
    return result

@router.get("/by-level/{level_id}", status_code=status.HTTP_200_OK)
async def get_sublevels_by_level(
    level_id: int,
    request: Request,
    db: Session = Depends(get_db),
    include_deleted: bool = Query(False),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get all sublevels for specific level - Admin/Moderator only"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_sublevels_by_level(
        level_id,
        include_deleted=include_deleted
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@router.get("/{sublevel_id}", status_code=status.HTTP_200_OK, response_model=SubLevelResponse)
async def get_sublevel(
    sublevel_id: int,
    request: Request,
    db: Session = Depends(get_db),
    include_deleted: bool = Query(False),
    current_user = Depends(require_moderator_or_admin)
) -> Dict[str, Any]:
    """Get sublevel by ID - Admin/Moderator only"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_sublevel(sublevel_id, include_deleted=include_deleted)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

# ✅ Bulk operations with both JSON and Form support
@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_sublevels(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    bulk_data: Optional[SubLevelBulkDeleteRequest] = None,
    # Form data (optional)
    ids: Optional[str] = Form(None, description="Comma-separated sublevel IDs"),
    permanent: Optional[bool] = Form(False, description="Permanent delete")
) -> Dict[str, Any]:
    """Bulk delete sublevels - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if bulk_data is not None:
        # JSON input
        sublevel_ids = bulk_data.ids
        is_permanent = bulk_data.permanent
    elif ids is not None:
        # Form data input
        try:
            sublevel_ids = [int(id_str.strip()) for id_str in ids.split(",") if id_str.strip()]
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
    
    if not sublevel_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one sublevel ID is required"
        )
    
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.bulk_delete_sublevels(
        sublevel_ids=sublevel_ids,
        permanent=is_permanent
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/bulk-restore", status_code=status.HTTP_200_OK)
async def bulk_restore_sublevels(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(require_moderator_or_admin),
    # JSON body (optional)
    bulk_data: Optional[SubLevelBulkRestoreRequest] = None,
    # Form data (optional)
    ids: Optional[str] = Form(None, description="Comma-separated sublevel IDs")
) -> Dict[str, Any]:
    """Bulk restore sublevels - Admin/Moderator only (supports JSON and Form data)"""
    
    # Determine input source
    if bulk_data is not None:
        # JSON input
        sublevel_ids = bulk_data.ids
    elif ids is not None:
        # Form data input
        try:
            sublevel_ids = [int(id_str.strip()) for id_str in ids.split(",") if id_str.strip()]
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
    
    if not sublevel_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one sublevel ID is required"
        )
    
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.bulk_restore_sublevels(sublevel_ids=sublevel_ids)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result