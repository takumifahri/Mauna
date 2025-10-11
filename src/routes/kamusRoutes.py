from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..config.middleware import require_moderator_or_admin
from ..handler.admin.master_kamus import Kamus_Management
from ..dto.kamus_dto import (
    KamusCreateRequest, KamusUpdateRequest, KamusResponse,
    KamusListResponse, KamusCategoryEnum
)

router = APIRouter(
    prefix="/kamus",
    tags=["Admin - Kamus Management"],
    # dependencies=[Depends(require_moderator_or_admin)]
)

@router.get("/", response_model=KamusListResponse)
async def get_all_kamus(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    include_deleted: bool = Query(False),
    category: Optional[KamusCategoryEnum] = Query(None, description="Filter by category"),
    # current_user = Depends(require_moderator_or_admin)
):
    """Get all kamus entries with optional category filter"""
    kamus_manager = Kamus_Management(db)
    result = kamus_manager.get_all_kamus(
        limit=limit,
        offset=offset,
        include_deleted=include_deleted,
        category=category.value if category else None
    )
    return result

@router.get("/statistics")
async def get_kamus_statistics(
    db: Session = Depends(get_db),
    # current_user = Depends(require_moderator_or_admin)
):
    """Get kamus statistics by category"""
    kamus_manager = Kamus_Management(db)
    return kamus_manager.get_kamus_statistics()