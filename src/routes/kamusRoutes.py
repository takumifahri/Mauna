from fastapi import Form, APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..handler.admin.master_kamus import KamusHandler
from ..config.middleware import require_moderator_or_admin
from ..dto.kamus_dto import KamusCreateDTO, KamusUpdateDTO, KamusResponseDTO, KamusListResponseDTO

router = APIRouter(
    prefix="/kamus",
    tags=["Kamus"],
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)

def get_kamus_handler(db: Session = Depends(get_db)) -> KamusHandler:
    return KamusHandler(db)

@router.post("/", response_model=KamusResponseDTO)
async def create_kamus(
    word_text: str = Form(...),
    definition: str = Form(...),
    video_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    handler: KamusHandler = Depends(get_kamus_handler),
    current_user=Depends(require_moderator_or_admin)
):
    result = handler.create_kamus(word_text, definition, image, video_url)
    return result["data"]

@router.get("/", response_model=KamusListResponseDTO)
def list_kamus(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    handler: KamusHandler = Depends(get_kamus_handler),
    current_user=Depends(require_moderator_or_admin)
):
    result = handler.list_kamus(skip, limit)
    return {
        "kamus": result["data"],
        "total": len(result["data"]),
        "skip": skip,
        "limit": limit
    }

@router.get("/{kamus_id}", response_model=KamusResponseDTO)
def get_kamus(
    kamus_id: int,
    request: Request,
    handler: KamusHandler = Depends(get_kamus_handler),
    current_user=Depends(require_moderator_or_admin)
):
    result = handler.get_kamus(kamus_id)
    return result["data"]

@router.put("/{kamus_id}", response_model=KamusResponseDTO)
async def update_kamus(
    kamus_id: int,
    request: Request,
    word_text: Optional[str] = Query(None),
    definition: Optional[str] = Query(None),
    image: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Query(None),
    handler: KamusHandler = Depends(get_kamus_handler),
    current_user=Depends(require_moderator_or_admin)
):
    result = handler.update_kamus(kamus_id, word_text, definition, image, video_url)
    return result["data"]

@router.delete("/{kamus_id}", response_model=dict)
def delete_kamus(
    kamus_id: int,
    request: Request,
    handler: KamusHandler = Depends(get_kamus_handler),
    current_user=Depends(require_moderator_or_admin)
):
    return handler.delete_kamus(kamus_id)