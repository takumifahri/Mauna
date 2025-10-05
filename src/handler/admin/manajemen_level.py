import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from dotenv import load_dotenv

from ...models.level import Level
from ...models.sublevel import SubLevel
from ...models.progress import Progress

load_dotenv()

class Level_Management:
    def __init__(self, db: Session):
        self.db = db

    def get_level(self, level_id: int, include_deleted: bool = False) -> Dict[str, Any]:
        """Get level by ID with consistent response format"""
        query = self.db.query(Level).filter(Level.id == level_id)
        
        if not include_deleted:
            query = query.filter(Level.deleted_at.is_(None))
        
        level = query.first()
        
        if not level:
            return {
                "success": False,
                "message": f"Level with ID {level_id} not found",
                "data": None
            }
        
        # ✅ Consistent field handling
        level_dict = {
            "id": level.id,
            "name": level.name,
            "description": level.description,
            "tujuan": level.tujuan,
            "total_sublevels": level.total_sublevels,
            "is_deleted": level.deleted_at is not None,
            "created_at": level.created_at,
            "updated_at": level.updated_at,
            "deleted_at": level.deleted_at
        }
        
        return {
            "success": True,
            "message": "Level retrieved successfully",
            "data": level_dict
        }

    def get_all_levels(self, limit: int = 100, offset: int = 0, include_deleted: bool = False) -> Dict[str, Any]:
        """Get all levels with pagination and consistent response format"""
        try:
            query = self.db.query(Level)
            
            # Filter deleted/active
            if not include_deleted:
                query = query.filter(Level.deleted_at.is_(None))
            
            total_count = query.count()
            levels = query.offset(offset).limit(limit).all()
            
            result = []
            for level in levels:
                level_dict = {
                    "id": level.id,
                    "name": level.name,
                    "description": level.description,
                    "tujuan": level.tujuan,
                    "total_sublevels": level.total_sublevels,
                    "is_deleted": level.deleted_at is not None,
                    "created_at": level.created_at,
                    "updated_at": level.updated_at,
                    "deleted_at": level.deleted_at
                }
                result.append(level_dict)
            
            return {
                "success": True,
                "message": f"Retrieved {len(result)} levels successfully",
                "data": result,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": (offset + limit) < total_count,
                    "has_prev": offset > 0
                },
                "filters": {
                    "include_deleted": include_deleted
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve levels: {str(e)}",
                "data": []
            }

    def search_levels(self, query: str, limit: int = 10, offset: int = 0, include_deleted: bool = False) -> Dict[str, Any]:
        """Search levels by name, description, or objective"""
        try:
            search_query = self.db.query(Level).filter(
                or_(
                    Level.name.ilike(f"%{query}%"),
                    Level.description.ilike(f"%{query}%"),
                    Level.tujuan.ilike(f"%{query}%")
                )
            )
            
            if not include_deleted:
                search_query = search_query.filter(Level.deleted_at.is_(None))
            
            total_count = search_query.count()
            levels = search_query.offset(offset).limit(limit).all()
            
            result = []
            for level in levels:
                level_dict = {
                    "id": level.id,
                    "name": level.name,
                    "description": level.description,
                    "tujuan": level.tujuan,
                    "total_sublevels": level.total_sublevels,
                    "is_deleted": level.deleted_at is not None,
                    "created_at": level.created_at,
                    "updated_at": level.updated_at,
                    "deleted_at": level.deleted_at
                }
                result.append(level_dict)
            
            return {
                "success": True,
                "message": f"Found {len(result)} levels matching '{query}'",
                "data": result,
                "search": {
                    "query": query,
                    "total_found": total_count,
                    "limit": limit,
                    "offset": offset,
                    "include_deleted": include_deleted
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Search failed: {str(e)}",
                "data": []
            }

    def create_level(self, level_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new level with consistent response format"""
        try:
            # Check if level name already exists
            existing = self.db.query(Level).filter(
                Level.name == level_data.get('name'),
                Level.deleted_at.is_(None)
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "message": f"Level with name '{level_data.get('name')}' already exists",
                    "data": None
                }
            
            new_level = Level(**level_data)
            self.db.add(new_level)
            self.db.commit()
            self.db.refresh(new_level)
            
            # ✅ Consistent response format
            level_dict = {
                "id": new_level.id,
                "name": new_level.name,
                "description": new_level.description,
                "tujuan": new_level.tujuan,
                "total_sublevels": 0,
                "is_deleted": False,
                "created_at": new_level.created_at,
                "updated_at": new_level.updated_at,
                "deleted_at": None
            }
            
            return {
                "success": True,
                "message": f"Level '{new_level.name}' created successfully",
                "data": level_dict
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to create level: {str(e)}",
                "data": None
            }

    def update_level(self, level_id: int, level_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update level data with consistent response format"""
        try:
            level = self.db.query(Level).filter(
                Level.id == level_id,
                Level.deleted_at.is_(None)
            ).first()
            
            if not level:
                return {
                    "success": False,
                    "message": f"Level with ID {level_id} not found or already deleted",
                    "data": None
                }
            
            # If updating name, check for duplicates
            if 'name' in level_data:
                existing = self.db.query(Level).filter(
                    Level.name == level_data['name'],
                    Level.id != level_id,
                    Level.deleted_at.is_(None)
                ).first()
                
                if existing:
                    return {
                        "success": False,
                        "message": f"Level with name '{level_data['name']}' already exists",
                        "data": None
                    }
            
            original_name = level.name
            
            # Update fields
            for key, value in level_data.items():
                if hasattr(level, key) and value is not None:
                    setattr(level, key, value)
            
            setattr(level, 'updated_at', datetime.utcnow())
            self.db.commit()
            self.db.refresh(level)
            
            # ✅ Consistent response format
            level_dict = {
                "id": level.id,
                "name": level.name,
                "description": level.description,
                "tujuan": level.tujuan,
                "total_sublevels": level.total_sublevels,
                "is_deleted": False,
                "created_at": level.created_at,
                "updated_at": level.updated_at,
                "deleted_at": None
            }
            
            return {
                "success": True,
                "message": f"Level '{original_name}' updated successfully",
                "data": level_dict
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to update level: {str(e)}",
                "data": None
            }

    def delete_level(self, level_id: int, permanent: bool = False) -> Dict[str, Any]:
        """Soft delete or permanent delete level"""
        try:
            level = self.db.query(Level).filter(Level.id == level_id).first()
            
            if not level:
                return {
                    "success": False,
                    "message": f"Level with ID {level_id} not found",
                    "data": None
                }
            
            if permanent:
                # Permanent delete - cascade delete all related data
                level_name = level.name
                
                # Get all sublevels in this level
                sublevels = self.db.query(SubLevel).filter(SubLevel.level_id == level_id).all()
                sublevel_count = len(sublevels)
                
                # Delete all progress records for sublevels in this level
                for sublevel in sublevels:
                    self.db.query(Progress).filter(Progress.sublevel_id == sublevel.id).delete()
                
                # Delete the level (sublevels will cascade delete due to relationship)
                self.db.delete(level)
                self.db.commit()
                
                return {
                    "success": True,
                    "message": f"Level '{level_name}' and {sublevel_count} sublevels permanently deleted",
                    "data": {
                        "deleted_level_id": level_id,
                        "deleted_level_name": level_name,
                        "deleted_sublevels_count": sublevel_count,
                        "deletion_type": "permanent",
                        "deleted_at": datetime.utcnow().isoformat()
                    }
                }
            else:
                # Soft delete
                if level.deleted_at is not None:
                    return {
                        "success": False,
                        "message": f"Level '{level.name}' is already deleted",
                        "data": None
                    }
                
                level_name = level.name
                
                # Soft delete level
                setattr(level, 'deleted_at', datetime.utcnow())
                setattr(level, 'updated_at', datetime.utcnow())
                
                # Also soft delete all sublevels in this level
                sublevels = self.db.query(SubLevel).filter(
                    SubLevel.level_id == level_id,
                    SubLevel.deleted_at.is_(None)
                ).all()
                
                sublevel_count = 0
                for sublevel in sublevels:
                    setattr(sublevel, 'deleted_at', datetime.utcnow())
                    setattr(sublevel, 'updated_at', datetime.utcnow())
                    sublevel_count += 1
                
                self.db.commit()
                
                return {
                    "success": True,
                    "message": f"Level '{level_name}' and {sublevel_count} sublevels soft deleted successfully",
                    "data": {
                        "deleted_level_id": level_id,
                        "deleted_level_name": level_name,
                        "deleted_sublevels_count": sublevel_count,
                        "deletion_type": "soft",
                        "deleted_at": level.deleted_at.isoformat()
                    }
                }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to delete level: {str(e)}",
                "data": None
            }

    def restore_level(self, level_id: int) -> Dict[str, Any]:
        """Restore soft deleted level"""
        try:
            level = self.db.query(Level).filter(
                Level.id == level_id,
                Level.deleted_at.is_not(None)
            ).first()
            
            if not level:
                return {
                    "success": False,
                    "message": f"Level with ID {level_id} not found in deleted records",
                    "data": None
                }
            
            level_name = level.name
            
            # Restore level
            setattr(level, 'deleted_at', None)
            setattr(level, 'updated_at', datetime.utcnow())
            
            # Also restore all sublevels in this level
            sublevels = self.db.query(SubLevel).filter(
                SubLevel.level_id == level_id,
                SubLevel.deleted_at.is_not(None)
            ).all()
            
            sublevel_count = 0
            for sublevel in sublevels:
                setattr(sublevel, 'deleted_at', None)
                setattr(sublevel, 'updated_at', datetime.utcnow())
                sublevel_count += 1
            
            self.db.commit()
            self.db.refresh(level)
            
            return {
                "success": True,
                "message": f"Level '{level_name}' and {sublevel_count} sublevels restored successfully",
                "data": {
                    "restored_level_id": level_id,
                    "restored_level_name": level_name,
                    "restored_sublevels_count": sublevel_count,
                    "restored_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to restore level: {str(e)}",
                "data": None
            }

    def get_deleted_levels(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get all soft deleted levels"""
        try:
            query = self.db.query(Level).filter(Level.deleted_at.is_not(None))
            total_count = query.count()
            levels = query.offset(offset).limit(limit).all()
            
            result = []
            for level in levels:
                level_dict = {
                    "id": level.id,
                    "name": level.name,
                    "description": level.description,
                    "tujuan": level.tujuan,
                    "total_sublevels": level.total_sublevels,
                    "is_deleted": True,
                    "created_at": level.created_at,
                    "updated_at": level.updated_at,
                    "deleted_at": level.deleted_at
                }
                result.append(level_dict)
            
            return {
                "success": True,
                "message": f"Retrieved {len(result)} deleted levels",
                "data": result,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": (offset + limit) < total_count,
                    "has_prev": offset > 0
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve deleted levels: {str(e)}",
                "data": []
            }

    def get_level_statistics(self) -> Dict[str, Any]:
        """Get level statistics"""
        try:
            total_levels = self.db.query(Level).count()
            active_levels = self.db.query(Level).filter(Level.deleted_at.is_(None)).count()
            deleted_levels = self.db.query(Level).filter(Level.deleted_at.is_not(None)).count()
            
            # Get levels with most sublevels
            levels_with_sublevels = self.db.query(Level).filter(Level.deleted_at.is_(None)).all()
            sublevel_stats = []
            for level in levels_with_sublevels:
                sublevel_count = level.total_sublevels
                sublevel_stats.append({
                    "level_id": level.id,
                    "level_name": level.name,
                    "total_sublevels": sublevel_count
                })
            
            # Sort by sublevel count descending
            sublevel_stats.sort(key=lambda x: x["total_sublevels"], reverse=True)
            
            # Get recent levels (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_levels = self.db.query(Level).filter(
                Level.created_at >= thirty_days_ago,
                Level.deleted_at.is_(None)
            ).count()
            
            stats_data = {
                "total_levels": total_levels,
                "active_levels": active_levels,
                "deleted_levels": deleted_levels,
                "recent_levels": recent_levels,
                "top_levels_by_sublevels": sublevel_stats[:10],  # Top 10
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "message": "Level statistics retrieved successfully",
                "data": stats_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve level statistics: {str(e)}",
                "data": {}
            }

    def bulk_delete_levels(self, level_ids: List[int], permanent: bool = False) -> Dict[str, Any]:
        """Bulk delete levels (soft or permanent)"""
        try:
            levels = self.db.query(Level).filter(Level.id.in_(level_ids)).all()
            
            if not levels:
                return {
                    "success": False,
                    "message": "No levels found with provided IDs",
                    "data": {
                        "processed_count": 0,
                        "deleted_count": 0,
                        "level_ids": level_ids
                    }
                }
            
            deleted_count = 0
            deleted_levels = []
            total_sublevels_affected = 0
            
            for level in levels:
                if permanent:
                    # Count sublevels before deletion
                    sublevels = self.db.query(SubLevel).filter(SubLevel.level_id == level.id).all()
                    sublevel_count = len(sublevels)
                    total_sublevels_affected += sublevel_count
                    
                    # Delete progress records for all sublevels
                    for sublevel in sublevels:
                        self.db.query(Progress).filter(Progress.sublevel_id == sublevel.id).delete()
                    
                    deleted_levels.append({
                        "id": level.id,
                        "name": level.name,
                        "sublevels_count": sublevel_count
                    })
                    self.db.delete(level)
                    deleted_count += 1
                else:
                    if level.deleted_at is None:  # Only soft delete if not already deleted
                        # Count active sublevels
                        sublevels = self.db.query(SubLevel).filter(
                            SubLevel.level_id == level.id,
                            SubLevel.deleted_at.is_(None)
                        ).all()
                        sublevel_count = len(sublevels)
                        total_sublevels_affected += sublevel_count
                        
                        # Soft delete level and sublevels
                        setattr(level, 'deleted_at', datetime.utcnow())
                        setattr(level, 'updated_at', datetime.utcnow())
                        
                        for sublevel in sublevels:
                            setattr(sublevel, 'deleted_at', datetime.utcnow())
                            setattr(sublevel, 'updated_at', datetime.utcnow())
                        
                        deleted_levels.append({
                            "id": level.id,
                            "name": level.name,
                            "sublevels_count": sublevel_count
                        })
                        deleted_count += 1
            
            self.db.commit()
            
            deletion_type = "permanently" if permanent else "soft"
            
            return {
                "success": True,
                "message": f"Successfully {deletion_type} deleted {deleted_count} levels and {total_sublevels_affected} sublevels",
                "data": {
                    "total_processed": len(levels),
                    "deleted_count": deleted_count,
                    "skipped_count": len(levels) - deleted_count,
                    "deletion_type": deletion_type,
                    "deleted_levels": deleted_levels,
                    "total_sublevels_affected": total_sublevels_affected,
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Bulk deletion failed: {str(e)}",
                "data": {
                    "processed_count": 0,
                    "deleted_count": 0,
                    "level_ids": level_ids
                }
            }

    def bulk_restore_levels(self, level_ids: List[int]) -> Dict[str, Any]:
        """Bulk restore soft deleted levels"""
        try:
            levels = self.db.query(Level).filter(
                Level.id.in_(level_ids),
                Level.deleted_at.is_not(None)
            ).all()
            
            if not levels:
                return {
                    "success": False,
                    "message": "No deleted levels found with provided IDs",
                    "data": {
                        "processed_count": 0,
                        "restored_count": 0,
                        "level_ids": level_ids
                    }
                }
            
            restored_count = 0
            restored_levels = []
            total_sublevels_restored = 0
            
            for level in levels:
                # Count deleted sublevels that will be restored
                sublevels = self.db.query(SubLevel).filter(
                    SubLevel.level_id == level.id,
                    SubLevel.deleted_at.is_not(None)
                ).all()
                sublevel_count = len(sublevels)
                total_sublevels_restored += sublevel_count
                
                # Restore level
                setattr(level, 'deleted_at', None)
                setattr(level, 'updated_at', datetime.utcnow())
                
                # Restore sublevels
                for sublevel in sublevels:
                    setattr(sublevel, 'deleted_at', None)
                    setattr(sublevel, 'updated_at', datetime.utcnow())
                
                restored_levels.append({
                    "id": level.id,
                    "name": level.name,
                    "sublevels_count": sublevel_count
                })
                restored_count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Successfully restored {restored_count} levels and {total_sublevels_restored} sublevels",
                "data": {
                    "total_processed": len(levels),
                    "restored_count": restored_count,
                    "restored_levels": restored_levels,
                    "total_sublevels_restored": total_sublevels_restored,
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Bulk restore failed: {str(e)}",
                "data": {
                    "processed_count": 0,
                    "restored_count": 0,
                    "level_ids": level_ids
                }
            }

    def get_level_with_sublevels(self, level_id: int, include_deleted: bool = False) -> Dict[str, Any]:
        """Get level with all its sublevels"""
        try:
            level = self.db.query(Level).filter(Level.id == level_id).first()
            if not level:
                return {
                    "success": False,
                    "message": f"Level with ID {level_id} not found",
                    "data": None
                }
            
            # Get sublevels
            query = self.db.query(SubLevel).filter(SubLevel.level_id == level_id)
            if not include_deleted:
                query = query.filter(SubLevel.deleted_at.is_(None))
            
            sublevels = query.order_by(SubLevel.id).all()
            
            sublevel_data = []
            for sublevel in sublevels:
                sublevel_dict = {
                    "id": sublevel.id,
                    "name": sublevel.name,
                    "description": sublevel.description,
                    "tujuan": sublevel.tujuan,
                    "total_soal": sublevel.total_soal,
                    "is_deleted": sublevel.deleted_at is not None,
                    "created_at": sublevel.created_at,
                    "updated_at": sublevel.updated_at,
                    "deleted_at": sublevel.deleted_at
                }
                sublevel_data.append(sublevel_dict)
            
            level_dict = {
                "id": level.id,
                "name": level.name,
                "description": level.description,
                "tujuan": level.tujuan,
                "total_sublevels": len(sublevel_data),
                "is_deleted": level.deleted_at is not None,
                "created_at": level.created_at,
                "updated_at": level.updated_at,
                "deleted_at": level.deleted_at,
                "sublevels": sublevel_data
            }
            
            return {
                "success": True,
                "message": f"Level '{level.name}' with {len(sublevel_data)} sublevels retrieved successfully",
                "data": level_dict
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve level with sublevels: {str(e)}",
                "data": None
            }