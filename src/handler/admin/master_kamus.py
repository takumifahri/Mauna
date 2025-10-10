from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_

from ...models.kamus import Kamus
from ...models.soal import Soal

class Kamus_Management:
    """Handler for Kamus management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_kamus(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new kamus entry"""
        try:
            # Check duplicate word_text
            existing = self.db.query(Kamus).filter(
                Kamus.word_text == data["word_text"],
                Kamus.deleted_at.is_(None)
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "message": f"Word '{data['word_text']}' already exists in dictionary"
                }
            
            # ✅ Handle category - default to ALPHABET
            category = data.get("category", "alphabet")
            if isinstance(category, str):
                # Convert string to enum
                try:
                    category_enum = Kamus.CategoryEnum[category.upper()]
                    # ✅ Handle category - convert to uppercase for database
                    category = data.get("category", "alphabet")
                    if isinstance(category, str):
                        category_enum = Kamus.CategoryEnum[category.upper()]
                    else:
                        category_enum = category
                    
                    new_kamus = Kamus(
                        word_text=data["word_text"],
                        definition=data["definition"],
                        category=category_enum,  # ✅ Will be stored as uppercase
                        image_url_ref=data.get("image_url_ref"),
                        video_url=data.get("video_url")
                    )
                    
                except KeyError:
                    category_enum = Kamus.CategoryEnum.ALPHABET
            else:
                category_enum = category
            
            # Create kamus
            new_kamus = Kamus(
                word_text=data["word_text"],
                definition=data["definition"],
                category=category_enum,
                image_url_ref=data.get("image_url_ref"),
                video_url=data.get("video_url")
            )
            
            self.db.add(new_kamus)
            self.db.commit()
            self.db.refresh(new_kamus)
            
            return {
                "success": True,
                "message": "Kamus entry created successfully",
                "data": {
                    "id": new_kamus.id,
                    "word_text": new_kamus.word_text,
                    "definition": new_kamus.definition,
                    "category": new_kamus.category.value,
                    "category_display": new_kamus.get_category_display(),
                    "image_url_ref": new_kamus.image_url_ref,
                    "video_url": new_kamus.video_url,
                    "total_soal": new_kamus.total_soal,
                    "created_at": new_kamus.created_at.isoformat() if new_kamus.created_at is not None else None
                }
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to create kamus entry: {str(e)}"
            }
    
    def get_all_kamus(
        self,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False,
        category: Optional[str] = None  # ✅ Filter by category
    ) -> Dict[str, Any]:
        """Get all kamus entries with optional category filter"""
        try:
            query = self.db.query(Kamus)
            
            # Filter deleted
            if not include_deleted:
                query = query.filter(Kamus.deleted_at.is_(None))
            
            # ✅ Filter by category
            if category:
                try:
                    category_enum = Kamus.CategoryEnum[category.upper()]
                    query = query.filter(Kamus.category == category_enum)
                except KeyError:
                    return {
                        "success": False,
                        "message": f"Invalid category: {category}. Valid: alphabet, numbers, imbuhan"
                    }
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            kamus_list = query.order_by(Kamus.word_text.asc()).offset(offset).limit(limit).all()
            
            return {
                "success": True,
                "message": f"Retrieved {len(kamus_list)} kamus entries",
                "data": [
                    {
                        "id": k.id,
                        "word_text": k.word_text,
                        "definition": k.definition,
                        "category": k.category.value,
                        "category_display": k.get_category_display(),
                        "image_url_ref": k.image_url_ref,
                        "video_url": k.video_url,
                        "total_soal": k.total_soal,
                        "created_at": k.created_at.isoformat() if k.created_at is not None else None,
                        "deleted_at": k.deleted_at.isoformat() if k.deleted_at is not None else None
                    }
                    for k in kamus_list
                ],
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve kamus entries: {str(e)}"
            }
    
    # ✅ Get statistics by category
    def get_kamus_statistics(self) -> Dict[str, Any]:
        """Get kamus statistics grouped by category"""
        try:
            total_kamus = self.db.query(func.count(Kamus.id)).filter(
                Kamus.deleted_at.is_(None)
            ).scalar() or 0
            
            # Count by category
            category_stats = {}
            for cat in Kamus.CategoryEnum:
                count = self.db.query(func.count(Kamus.id)).filter(
                    Kamus.category == cat,
                    Kamus.deleted_at.is_(None)
                ).scalar() or 0
                
                category_stats[cat.value] = {
                    "count": count,
                    "percentage": round((count / total_kamus * 100), 2) if total_kamus > 0 else 0,
                    "display_name": Kamus(category=cat).get_category_display()
                }
            
            deleted_count = self.db.query(func.count(Kamus.id)).filter(
                Kamus.deleted_at.isnot(None)
            ).scalar() or 0
            
            return {
                "success": True,
                "message": "Statistics retrieved successfully",
                "data": {
                    "total_active": total_kamus,
                    "total_deleted": deleted_count,
                    "by_category": category_stats
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get statistics: {str(e)}"
            }