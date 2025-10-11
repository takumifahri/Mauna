from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from ..database import get_db
from ..models.badges import Badge
from ..models.kamus import Kamus
from ..models.level import Level
from ..models.sublevel import SubLevel
from ..models.soal import Soal
from ..handler.admin.master_kamus import Kamus_Management
from ..handler.admin.manajemen_level import Level_Management
from ..handler.admin.manajemen_sublevel import SubLevel_Management
from ..handler.admin.Manajemen_soal import SoalHandler

# ✅ PUBLIC ROUTER - No authentication required
public_router = APIRouter(
    prefix="/public",
    tags=["🌍 Public - No Authentication Required"]
)

# =====================================================================
# BADGES - PUBLIC READ
# =====================================================================
@public_router.get("/badges")
async def get_public_badges(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """🌍 PUBLIC - Get all badges"""
    badges = db.query(Badge).offset(offset).limit(limit).all()
    
    return {
        "success": True,
        "total": db.query(Badge).count(),
        "data": [
            {
                "id": badge.id,
                "nama": badge.nama,
                "deskripsi": badge.deskripsi,
                "icon": badge.icon,
                "level": badge.level.value if badge.level is not None else None
            }
            for badge in badges
        ]
    }

@public_router.get("/badges/{badge_id}")
async def get_public_badge(
    badge_id: int,
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get badge by ID"""
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )
    
    return {
        "success": True,
        "data": {
            "id": badge.id,
            "nama": badge.nama,
            "deskripsi": badge.deskripsi,
            "icon": badge.icon,
            "level": badge.level.value if badge.level is not None else None
        }
    }

# =====================================================================
# KAMUS - PUBLIC READ
# =====================================================================
@public_router.get("/kamus")
async def get_public_kamus(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """🌍 PUBLIC - Get all kamus"""
    kamus_manager = Kamus_Management(db)
    result = kamus_manager.get_all_kamus(
        limit=limit,
        offset=offset,
        include_deleted=False,
        category=category
    )
    return result

@public_router.get("/kamus/{kamus_id}")
async def get_public_kamus_detail(
    kamus_id: int,
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get kamus by ID"""
    kamus = db.query(Kamus).filter(
        Kamus.id == kamus_id,
        Kamus.deleted_at.is_(None)
    ).first()
    
    if not kamus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kamus not found"
        )
    
    return {
        "success": True,
        "data": {
            "id": kamus.id,
            "word_text": kamus.word_text,
            "definition": kamus.definition,
            "video_url": kamus.video_url,
            "category": kamus.category,
            "total_soal": kamus.total_soal
        }
    }

@public_router.get("/kamus/statistics")
async def get_public_kamus_statistics(
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get kamus statistics"""
    kamus_manager = Kamus_Management(db)
    return kamus_manager.get_kamus_statistics()

# =====================================================================
# LEVELS - PUBLIC READ
# =====================================================================
@public_router.get("/levels")
async def get_public_levels(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """🌍 PUBLIC - Get all levels"""
    level_manager = Level_Management(db)
    result = level_manager.get_all_levels(
        limit=limit,
        offset=offset,
        include_deleted=False
    )
    return result

@public_router.get("/levels/{level_id}")
async def get_public_level(
    level_id: int,
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get level by ID"""
    level_manager = Level_Management(db)
    result = level_manager.get_level(level_id, include_deleted=False)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@public_router.get("/levels/{level_id}/with-sublevels")
async def get_public_level_with_sublevels(
    level_id: int,
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get level with all sublevels"""
    level_manager = Level_Management(db)
    result = level_manager.get_level_with_sublevels(level_id, include_deleted=False)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@public_router.get("/levels/statistics")
async def get_public_level_statistics(
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get level statistics"""
    level_manager = Level_Management(db)
    return level_manager.get_level_statistics()

# =====================================================================
# SUBLEVELS - PUBLIC READ
# =====================================================================
@public_router.get("/sublevels")
async def get_public_sublevels(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    level_id: Optional[int] = Query(None)
):
    """🌍 PUBLIC - Get all sublevels"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_all_sublevels(
        limit=limit,
        offset=offset,
        include_deleted=False,
        level_id=level_id
    )
    return result

@public_router.get("/sublevels/{sublevel_id}")
async def get_public_sublevel(
    sublevel_id: int,
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get sublevel by ID"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_sublevel(sublevel_id, include_deleted=False)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@public_router.get("/sublevels/by-level/{level_id}")
async def get_public_sublevels_by_level(
    level_id: int,
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get sublevels by level"""
    sublevel_manager = SubLevel_Management(db)
    result = sublevel_manager.get_sublevels_by_level(level_id, include_deleted=False)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result

@public_router.get("/sublevels/statistics")
async def get_public_sublevel_statistics(
    db: Session = Depends(get_db),
    level_id: Optional[int] = Query(None)
):
    """🌍 PUBLIC - Get sublevel statistics"""
    sublevel_manager = SubLevel_Management(db)
    return sublevel_manager.get_sublevel_statistics(level_id=level_id)

# =====================================================================
# SOAL - PUBLIC READ (List only, no detail)
# =====================================================================
@public_router.get("/soal/statistics")
async def get_public_soal_statistics(
    db: Session = Depends(get_db)
):
    """🌍 PUBLIC - Get soal statistics"""
    soal_handler = SoalHandler(db)
    return soal_handler.get_soal_statistics()

@public_router.get("/soal/helpers/available-kamus")
async def get_public_available_kamus(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None)
):
    """🌍 PUBLIC - Get available kamus for dropdown"""
    soal_handler = SoalHandler(db)
    return soal_handler.get_available_kamus(search)

@public_router.get("/soal/helpers/available-sublevels")
async def get_public_available_sublevels(
    db: Session = Depends(get_db),
    level_id: Optional[int] = Query(None)
):
    """🌍 PUBLIC - Get available sublevels for dropdown"""
    soal_handler = SoalHandler(db)
    return soal_handler.get_available_sublevels(level_id)

