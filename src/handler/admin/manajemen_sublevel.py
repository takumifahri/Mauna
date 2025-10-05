import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_
from dotenv import load_dotenv

from ...models.sublevel import SubLevel
from ...models.level import Level
from ...models.soal import Soal
from ...models.progress import Progress

load_dotenv()

class SubLevel_Management:
    def __init__(self, db: Session):
        self.db = db

    def get_sublevel(self, sublevel_id: int, include_deleted: bool = False) -> Dict[str, Any]:
        """Get sublevel by ID with consistent response format"""
        query = self.db.query(SubLevel).filter(SubLevel.id == sublevel_id)
        
        if not include_deleted:
            query = query.filter(SubLevel.deleted_at.is_(None))
        
        sublevel = query.first()
        
        if not sublevel:
            return {
                "success": False,
                "message": f"SubLevel with ID {sublevel_id} not found",
                "data": None
            }
        
        # ✅ Consistent field handling
        sublevel_dict = {
            "id": sublevel.id,
            "name": sublevel.name,
            "description": sublevel.description,
            "tujuan": sublevel.tujuan,
            "level_id": sublevel.level_id,
            "level_name": sublevel.level_ref.name if sublevel.level_ref else None,
            "total_soal": sublevel.total_soal,
            "is_deleted": sublevel.deleted_at is not None,
            "created_at": sublevel.created_at,
            "updated_at": sublevel.updated_at,
            "deleted_at": sublevel.deleted_at
        }
        
        return {
            "success": True,
            "message": "SubLevel retrieved successfully",
            "data": sublevel_dict
        }

    def get_all_sublevels(self, limit: int = 100, offset: int = 0, include_deleted: bool = False, level_id: Optional[int] = None) -> Dict[str, Any]:
        """Get all sublevels with pagination and consistent response format"""
        try:
            query = self.db.query(SubLevel)
            
            # Filter by level_id if provided
            if level_id:
                query = query.filter(SubLevel.level_id == level_id)
            
            # Filter deleted/active
            if not include_deleted:
                query = query.filter(SubLevel.deleted_at.is_(None))
            
            total_count = query.count()
            sublevels = query.offset(offset).limit(limit).all()
            
            result = []
            for sublevel in sublevels:
                sublevel_dict = {
                    "id": sublevel.id,
                    "name": sublevel.name,
                    "description": sublevel.description,
                    "tujuan": sublevel.tujuan,
                    "level_id": sublevel.level_id,
                    "level_name": sublevel.level_ref.name if sublevel.level_ref else None,
                    "total_soal": sublevel.total_soal,
                    "is_deleted": sublevel.deleted_at is not None,
                    "created_at": sublevel.created_at,
                    "updated_at": sublevel.updated_at,
                    "deleted_at": sublevel.deleted_at
                }
                result.append(sublevel_dict)
            
            return {
                "success": True,
                "message": f"Retrieved {len(result)} sublevels successfully",
                "data": result,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": (offset + limit) < total_count,
                    "has_prev": offset > 0
                },
                "filters": {
                    "level_id": level_id,
                    "include_deleted": include_deleted
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve sublevels: {str(e)}",
                "data": []
            }

    def search_sublevels(self, query: str, limit: int = 10, offset: int = 0, include_deleted: bool = False) -> Dict[str, Any]:
        """Search sublevels by name, description, or objective"""
        try:
            search_query = self.db.query(SubLevel).filter(
                or_(
                    SubLevel.name.ilike(f"%{query}%"),
                    SubLevel.description.ilike(f"%{query}%"),
                    SubLevel.tujuan.ilike(f"%{query}%")
                )
            )
            
            if not include_deleted:
                search_query = search_query.filter(SubLevel.deleted_at.is_(None))
            
            total_count = search_query.count()
            sublevels = search_query.offset(offset).limit(limit).all()
            
            result = []
            for sublevel in sublevels:
                sublevel_dict = {
                    "id": sublevel.id,
                    "name": sublevel.name,
                    "description": sublevel.description,
                    "tujuan": sublevel.tujuan,
                    "level_id": sublevel.level_id,
                    "level_name": sublevel.level_ref.name if sublevel.level_ref else None,
                    "total_soal": sublevel.total_soal,
                    "is_deleted": sublevel.deleted_at is not None,
                    "created_at": sublevel.created_at,
                    "updated_at": sublevel.updated_at,
                    "deleted_at": sublevel.deleted_at
                }
                result.append(sublevel_dict)
            
            return {
                "success": True,
                "message": f"Found {len(result)} sublevels matching '{query}'",
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

    def create_sublevel(self, sublevel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new sublevel with consistent response format"""
        try:
            # Validate level exists
            level = self.db.query(Level).filter(
                Level.id == sublevel_data.get('level_id'),
                Level.deleted_at.is_(None)
            ).first()
            
            if not level:
                return {
                    "success": False,
                    "message": f"Level with ID {sublevel_data.get('level_id')} not found or deleted",
                    "data": None
                }
            
            # Check if sublevel name already exists in this level
            existing = self.db.query(SubLevel).filter(
                SubLevel.name == sublevel_data.get('name'),
                SubLevel.level_id == sublevel_data.get('level_id'),
                SubLevel.deleted_at.is_(None)
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "message": f"SubLevel with name '{sublevel_data.get('name')}' already exists in level '{level.name}'",
                    "data": None
                }
            
            new_sublevel = SubLevel(**sublevel_data)
            self.db.add(new_sublevel)
            self.db.commit()
            self.db.refresh(new_sublevel)
            
            # ✅ Consistent response format
            sublevel_dict = {
                "id": new_sublevel.id,
                "name": new_sublevel.name,
                "description": new_sublevel.description,
                "tujuan": new_sublevel.tujuan,
                "level_id": new_sublevel.level_id,
                "level_name": new_sublevel.level_ref.name if new_sublevel.level_ref else None,
                "total_soal": 0,
                "is_deleted": False,
                "created_at": new_sublevel.created_at,
                "updated_at": new_sublevel.updated_at,
                "deleted_at": None
            }
            
            return {
                "success": True,
                "message": f"SubLevel '{new_sublevel.name}' created successfully in level '{level.name}'",
                "data": sublevel_dict
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to create sublevel: {str(e)}",
                "data": None
            }

    def update_sublevel(self, sublevel_id: int, sublevel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update sublevel data with consistent response format"""
        try:
            sublevel = self.db.query(SubLevel).filter(
                SubLevel.id == sublevel_id,
                SubLevel.deleted_at.is_(None)
            ).first()
            
            if not sublevel:
                return {
                    "success": False,
                    "message": f"SubLevel with ID {sublevel_id} not found or already deleted",
                    "data": None
                }
            
            # If updating level_id, validate new level exists
            if 'level_id' in sublevel_data:
                level = self.db.query(Level).filter(
                    Level.id == sublevel_data['level_id'],
                    Level.deleted_at.is_(None)
                ).first()
                
                if not level:
                    return {
                        "success": False,
                        "message": f"Level with ID {sublevel_data['level_id']} not found or deleted",
                        "data": None
                    }
            
            # If updating name, check for duplicates in the same level
            if 'name' in sublevel_data:
                level_id = sublevel_data.get('level_id', sublevel.level_id)
                existing = self.db.query(SubLevel).filter(
                    SubLevel.name == sublevel_data['name'],
                    SubLevel.level_id == level_id,
                    SubLevel.id != sublevel_id,
                    SubLevel.deleted_at.is_(None)
                ).first()
                
                if existing:
                    return {
                        "success": False,
                        "message": f"SubLevel with name '{sublevel_data['name']}' already exists in this level",
                        "data": None
                    }
            
            original_name = sublevel.name
            
            # Update fields
            for key, value in sublevel_data.items():
                if hasattr(sublevel, key) and value is not None:
                    setattr(sublevel, key, value)
            
            setattr(sublevel, 'updated_at', datetime.utcnow())
            self.db.commit()
            self.db.refresh(sublevel)
            
            # ✅ Consistent response format
            sublevel_dict = {
                "id": sublevel.id,
                "name": sublevel.name,
                "description": sublevel.description,
                "tujuan": sublevel.tujuan,
                "level_id": sublevel.level_id,
                "level_name": sublevel.level_ref.name if sublevel.level_ref else None,
                "total_soal": sublevel.total_soal,
                "is_deleted": False,
                "created_at": sublevel.created_at,
                "updated_at": sublevel.updated_at,
                "deleted_at": None
            }
            
            return {
                "success": True,
                "message": f"SubLevel '{original_name}' updated successfully",
                "data": sublevel_dict
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to update sublevel: {str(e)}",
                "data": None
            }

    def delete_sublevel(self, sublevel_id: int, permanent: bool = False) -> Dict[str, Any]:
        """Soft delete or permanent delete sublevel"""
        try:
            sublevel = self.db.query(SubLevel).filter(SubLevel.id == sublevel_id).first()
            
            if not sublevel:
                return {
                    "success": False,
                    "message": f"SubLevel with ID {sublevel_id} not found",
                    "data": None
                }
            
            if permanent:
                # Permanent delete - also delete related data
                sublevel_name = sublevel.name
                level_name = sublevel.level_ref.name if sublevel.level_ref else "Unknown"
                
                # Delete related progress records
                self.db.query(Progress).filter(Progress.sublevel_id == sublevel_id).delete()
                
                # Delete related soal (questions) - they should cascade delete
                self.db.delete(sublevel)
                self.db.commit()
                
                return {
                    "success": True,
                    "message": f"SubLevel '{sublevel_name}' from level '{level_name}' permanently deleted",
                    "data": {
                        "deleted_sublevel_id": sublevel_id,
                        "deleted_sublevel_name": sublevel_name,
                        "level_name": level_name,
                        "deletion_type": "permanent",
                        "deleted_at": datetime.utcnow().isoformat()
                    }
                }
            else:
                # Soft delete
                if sublevel.deleted_at is not None:
                    return {
                        "success": False,
                        "message": f"SubLevel '{sublevel.name}' is already deleted",
                        "data": None
                    }
                
                sublevel_name = sublevel.name
                level_name = sublevel.level_ref.name if sublevel.level_ref else "Unknown"
                
                setattr(sublevel, 'deleted_at', datetime.utcnow())
                setattr(sublevel, 'updated_at', datetime.utcnow())
                self.db.commit()
                
                return {
                    "success": True,
                    "message": f"SubLevel '{sublevel_name}' from level '{level_name}' soft deleted successfully",
                    "data": {
                        "deleted_sublevel_id": sublevel_id,
                        "deleted_sublevel_name": sublevel_name,
                        "level_name": level_name,
                        "deletion_type": "soft",
                        "deleted_at": sublevel.deleted_at.isoformat()
                    }
                }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to delete sublevel: {str(e)}",
                "data": None
            }

    def restore_sublevel(self, sublevel_id: int) -> Dict[str, Any]:
        """Restore soft deleted sublevel"""
        try:
            sublevel = self.db.query(SubLevel).filter(
                SubLevel.id == sublevel_id,
                SubLevel.deleted_at.is_not(None)
            ).first()
            
            if not sublevel:
                return {
                    "success": False,
                    "message": f"SubLevel with ID {sublevel_id} not found in deleted records",
                    "data": None
                }
            
            # Check if parent level is not deleted
            if sublevel.level_ref and sublevel.level_ref.deleted_at is not None:
                return {
                    "success": False,
                    "message": f"Cannot restore sublevel '{sublevel.name}' because parent level '{sublevel.level_ref.name}' is deleted",
                    "data": None
                }
            
            sublevel_name = sublevel.name
            level_name = sublevel.level_ref.name if sublevel.level_ref else "Unknown"
            
            setattr(sublevel, 'deleted_at', None)
            setattr(sublevel, 'updated_at', datetime.utcnow())
            self.db.commit()
            self.db.refresh(sublevel)
            
            return {
                "success": True,
                "message": f"SubLevel '{sublevel_name}' from level '{level_name}' restored successfully",
                "data": {
                    "restored_sublevel_id": sublevel_id,
                    "restored_sublevel_name": sublevel_name,
                    "level_name": level_name,
                    "restored_at": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to restore sublevel: {str(e)}",
                "data": None
            }

    def get_deleted_sublevels(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get all soft deleted sublevels"""
        try:
            query = self.db.query(SubLevel).filter(SubLevel.deleted_at.is_not(None))
            total_count = query.count()
            sublevels = query.offset(offset).limit(limit).all()
            
            result = []
            for sublevel in sublevels:
                sublevel_dict = {
                    "id": sublevel.id,
                    "name": sublevel.name,
                    "description": sublevel.description,
                    "tujuan": sublevel.tujuan,
                    "level_id": sublevel.level_id,
                    "level_name": sublevel.level_ref.name if sublevel.level_ref else None,
                    "total_soal": sublevel.total_soal,
                    "is_deleted": True,
                    "created_at": sublevel.created_at,
                    "updated_at": sublevel.updated_at,
                    "deleted_at": sublevel.deleted_at
                }
                result.append(sublevel_dict)
            
            return {
                "success": True,
                "message": f"Retrieved {len(result)} deleted sublevels",
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
                "message": f"Failed to retrieve deleted sublevels: {str(e)}",
                "data": []
            }

    def get_sublevel_statistics(self, level_id: Optional[int] = None) -> Dict[str, Any]:
        """Get sublevel statistics"""
        try:
            query = self.db.query(SubLevel)
            
            if level_id:
                query = query.filter(SubLevel.level_id == level_id)
            
            total_sublevels = query.count()
            active_sublevels = query.filter(SubLevel.deleted_at.is_(None)).count()
            deleted_sublevels = query.filter(SubLevel.deleted_at.is_not(None)).count()
            
            # Get sublevels with most soal
            sublevels_with_soal = query.filter(SubLevel.deleted_at.is_(None)).all()
            soal_stats = []
            for sublevel in sublevels_with_soal:
                soal_count = sublevel.total_soal
                soal_stats.append({
                    "sublevel_id": sublevel.id,
                    "sublevel_name": sublevel.name,
                    "level_name": sublevel.level_ref.name if sublevel.level_ref else None,
                    "total_soal": soal_count
                })
            
            # Sort by soal count descending
            soal_stats.sort(key=lambda x: x["total_soal"], reverse=True)
            
            # Get recent sublevels (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_sublevels = query.filter(
                SubLevel.created_at >= thirty_days_ago,
                SubLevel.deleted_at.is_(None)
            ).count()
            
            stats_data = {
                "total_sublevels": total_sublevels,
                "active_sublevels": active_sublevels,
                "deleted_sublevels": deleted_sublevels,
                "recent_sublevels": recent_sublevels,
                "top_sublevels_by_soal": soal_stats[:10],  # Top 10
                "level_filter": level_id,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "message": "SubLevel statistics retrieved successfully",
                "data": stats_data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve sublevel statistics: {str(e)}",
                "data": {}
            }

    def bulk_delete_sublevels(self, sublevel_ids: List[int], permanent: bool = False) -> Dict[str, Any]:
        """Bulk delete sublevels (soft or permanent)"""
        try:
            sublevels = self.db.query(SubLevel).filter(SubLevel.id.in_(sublevel_ids)).all()
            
            if not sublevels:
                return {
                    "success": False,
                    "message": "No sublevels found with provided IDs",
                    "data": {
                        "processed_count": 0,
                        "deleted_count": 0,
                        "sublevel_ids": sublevel_ids
                    }
                }
            
            deleted_count = 0
            deleted_sublevels = []
            
            for sublevel in sublevels:
                if permanent:
                    # Delete related progress records
                    self.db.query(Progress).filter(Progress.sublevel_id == sublevel.id).delete()
                    
                    deleted_sublevels.append({
                        "id": sublevel.id,
                        "name": sublevel.name,
                        "level_name": sublevel.level_ref.name if sublevel.level_ref else None
                    })
                    self.db.delete(sublevel)
                    deleted_count += 1
                else:
                    if sublevel.deleted_at is None:  # Only soft delete if not already deleted
                        setattr(sublevel, 'deleted_at', datetime.utcnow())
                        setattr(sublevel, 'updated_at', datetime.utcnow())
                        deleted_sublevels.append({
                            "id": sublevel.id,
                            "name": sublevel.name,
                            "level_name": sublevel.level_ref.name if sublevel.level_ref else None
                        })
                        deleted_count += 1
            
            self.db.commit()
            
            deletion_type = "permanently" if permanent else "soft"
            
            return {
                "success": True,
                "message": f"Successfully {deletion_type} deleted {deleted_count} out of {len(sublevels)} sublevels",
                "data": {
                    "total_processed": len(sublevels),
                    "deleted_count": deleted_count,
                    "skipped_count": len(sublevels) - deleted_count,
                    "deletion_type": deletion_type,
                    "deleted_sublevels": deleted_sublevels,
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
                    "sublevel_ids": sublevel_ids
                }
            }

    def bulk_restore_sublevels(self, sublevel_ids: List[int]) -> Dict[str, Any]:
        """Bulk restore soft deleted sublevels"""
        try:
            sublevels = self.db.query(SubLevel).filter(
                SubLevel.id.in_(sublevel_ids),
                SubLevel.deleted_at.is_not(None)
            ).all()
            
            if not sublevels:
                return {
                    "success": False,
                    "message": "No deleted sublevels found with provided IDs",
                    "data": {
                        "processed_count": 0,
                        "restored_count": 0,
                        "sublevel_ids": sublevel_ids
                    }
                }
            
            restored_count = 0
            restored_sublevels = []
            skipped_sublevels = []
            
            for sublevel in sublevels:
                # Check if parent level is not deleted
                if sublevel.level_ref and sublevel.level_ref.deleted_at is not None:
                    skipped_sublevels.append({
                        "id": sublevel.id,
                        "name": sublevel.name,
                        "reason": f"Parent level '{sublevel.level_ref.name}' is deleted"
                    })
                    continue
                
                setattr(sublevel, 'deleted_at', None)
                setattr(sublevel, 'updated_at', datetime.utcnow())
                restored_sublevels.append({
                    "id": sublevel.id,
                    "name": sublevel.name,
                    "level_name": sublevel.level_ref.name if sublevel.level_ref else None
                })
                restored_count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Successfully restored {restored_count} out of {len(sublevels)} sublevels",
                "data": {
                    "total_processed": len(sublevels),
                    "restored_count": restored_count,
                    "skipped_count": len(skipped_sublevels),
                    "restored_sublevels": restored_sublevels,
                    "skipped_sublevels": skipped_sublevels,
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
                    "sublevel_ids": sublevel_ids
                }
            }

    def get_sublevels_by_level(self, level_id: int, include_deleted: bool = False) -> Dict[str, Any]:
        """Get all sublevels for specific level"""
        try:
            # Validate level exists
            level = self.db.query(Level).filter(Level.id == level_id).first()
            if not level:
                return {
                    "success": False,
                    "message": f"Level with ID {level_id} not found",
                    "data": []
                }
            
            query = self.db.query(SubLevel).filter(SubLevel.level_id == level_id)
            
            if not include_deleted:
                query = query.filter(SubLevel.deleted_at.is_(None))
            
            sublevels = query.order_by(SubLevel.id).all()
            
            result = []
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
                result.append(sublevel_dict)
            
            return {
                "success": True,
                "message": f"Retrieved {len(result)} sublevels for level '{level.name}'",
                "data": {
                    "level_id": level_id,
                    "level_name": level.name,
                    "total_sublevels": len(result),
                    "sublevels": result
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve sublevels by level: {str(e)}",
                "data": []
            }