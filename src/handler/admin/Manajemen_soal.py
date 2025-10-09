from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, UploadFile
import os
import uuid
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json

from ...models.soal import Soal
from ...models.kamus import Kamus
from ...models.sublevel import SubLevel
from ...models.level import Level
from ...dto import (
    SoalCreateRequest, SoalUpdateRequest, SoalData, SoalListData,
    BulkDeleteSoalRequest, BulkRestoreSoalRequest
)

class SoalHandler:
    """Handler untuk manajemen soal (Questions Management) - CRUD + Soft Delete + Restore + Caching"""
    
    # Class-level cache untuk menyimpan hasil query
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_timestamps: Dict[str, datetime] = {}
    _cache_ttl = 180  # ✅ Cache TTL 3 minutes (180 seconds)
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================================
    # CACHE MANAGEMENT
    # =====================================================================
    
    @classmethod
    def _generate_cache_key(cls, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Sort kwargs untuk konsistensi
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        hash_str = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{hash_str}"
    
    @classmethod
    def _get_from_cache(cls, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid"""
        if cache_key not in cls._cache:
            return None
        
        # Check if cache is expired
        cache_time = cls._cache_timestamps.get(cache_key)
        if cache_time:
            age = (datetime.now(timezone.utc) - cache_time).total_seconds()
            if age > cls._cache_ttl:
                # Cache expired, remove it
                cls._cache.pop(cache_key, None)
                cls._cache_timestamps.pop(cache_key, None)
                return None
        
        return cls._cache.get(cache_key)
    
    @classmethod
    def _set_cache(cls, cache_key: str, data: Dict[str, Any]):
        """Set data to cache"""
        cls._cache[cache_key] = data
        cls._cache_timestamps[cache_key] = datetime.now(timezone.utc)
    
    @classmethod
    def _invalidate_cache(cls, prefix: Optional[str] = None):
        """Invalidate cache (all or by prefix)"""
        if prefix:
            # Remove only keys with specific prefix
            keys_to_remove = [k for k in cls._cache.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                cls._cache.pop(key, None)
                cls._cache_timestamps.pop(key, None)
        else:
            # Clear all cache
            cls._cache.clear()
            cls._cache_timestamps.clear()
    
    @classmethod
    def clear_all_cache(cls):
        """Manually clear all cache"""
        cls._invalidate_cache()
    
    # =====================================================================
    # HELPER METHODS FOR TYPE-SAFE CONVERSIONS
    # =====================================================================
    
    @staticmethod
    def _serialize_datetime(dt: Any) -> Optional[str]:
        """Convert datetime to ISO format string - type-safe version"""
        if dt is None:
            return None
        # Handle both datetime objects and Column[datetime]
        if isinstance(dt, datetime):
            return dt.isoformat()
        # If it's a Column, try to get the actual value
        try:
            if hasattr(dt, '__class__') and 'Column' in str(dt.__class__):
                return None  # Column without value
            return str(dt) if dt else None
        except:
            return None
    
    @staticmethod
    def _get_int_value(value: Any) -> int:
        """Safely extract int value from Column or int"""
        if value is None:
            return 0
        if isinstance(value, int):
            return value
        # Try to convert to int
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def _get_str_value(value: Any) -> str:
        """Safely extract string value from Column or str"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            return str(value)
        except:
            return ""
    
    @staticmethod
    def _get_optional_int(value: Any) -> Optional[int]:
        """Safely extract optional int value"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    # =====================================================================
    # CREATE - Buat soal baru
    # =====================================================================
   
    def create_soal(self, soal_data: SoalCreateRequest) -> Dict[str, Any]:
        """Create new soal"""
        try:
            # Validate foreign keys
            self._validate_foreign_keys(soal_data.sublevel_id, soal_data.dictionary_id)
            
            # Create soal object
            soal = Soal(
                question=soal_data.pertanyaan,
                answer=soal_data.jawaban_benar,
                video_url=soal_data.video_url,
                dictionary_id=soal_data.dictionary_id,
                sublevel_id=soal_data.sublevel_id
            )
            
            self.db.add(soal)
            self.db.commit()
            self.db.refresh(soal)
            
            # ✅ Invalidate cache after create
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            # Get detailed data for response - type-safe
            soal_id = self._get_int_value(soal.id)
            if soal_id == 0:
                raise ValueError("Failed to get soal ID after creation")
                
            soal_detail = self._get_soal_detail(soal_id)
            
            return {
                "success": True,
                "message": "Soal berhasil dibuat",
                "data": soal_detail
            }
            
        except ValueError as ve:
            self.db.rollback()
            return {
                "success": False,
                "message": str(ve),
                "data": None
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal membuat soal: {str(e)}",
                "data": None
            }
    
    # =====================================================================
    # READ - Ambil data soal
    # =====================================================================
    def get_soal(self, soal_id: int) -> Dict[str, Any]:
        """Get single soal by ID"""
        try:
            soal_detail = self._get_soal_detail(soal_id)
            
            if not soal_detail:
                return {
                    "success": False,
                    "message": "Soal tidak ditemukan",
                    "data": None
                }
            
            return {
                "success": True,
                "message": "Soal berhasil diambil",
                "data": soal_detail
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal mengambil soal: {str(e)}",
                "data": None
            }
    
    def list_soal(
        self,
        search: Optional[str] = None,
        sublevel_id: Optional[int] = None,
        level_id: Optional[int] = None,
        dictionary_id: Optional[int] = None,
        include_deleted: bool = False,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        use_cache: bool = True  # ✅ Cache control
    ) -> Dict[str, Any]:
        """
        ✅ List ALL soal tanpa pagination dengan caching 3 menit
        
        - Cache TTL: 3 menit (180 detik)
        - Menampilkan semua data sekaligus
        - Include image_url & video_url dari database
        """
        try:
            # ✅ Generate cache key
            cache_key = self._generate_cache_key(
                "soal_list",
                search=search,
                sublevel_id=sublevel_id,
                level_id=level_id,
                dictionary_id=dictionary_id,
                include_deleted=include_deleted,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            # ✅ Check cache first
            if use_cache:
                cached_data = self._get_from_cache(cache_key)
                if cached_data:
                    # Mark as cached and return
                    cached_data["cached"] = True
                    cache_timestamp = self._cache_timestamps.get(cache_key)
                    if cache_timestamp:
                        cached_data["cache_age_seconds"] = int(
                            (datetime.now(timezone.utc) - cache_timestamp).total_seconds()
                        )
                    return cached_data
            
            # Base query dengan joins
            query = self.db.query(Soal).options(
                joinedload(Soal.kamus_ref),
                joinedload(Soal.sublevel_ref).joinedload(SubLevel.level_ref)
            )
            
            # Filter soft delete
            if not include_deleted:
                query = query.filter(Soal.deleted_at.is_(None))
            
            # Search filter
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Soal.question.ilike(search_filter),
                        Soal.answer.ilike(search_filter)
                    )
                )
            
            # SubLevel filter
            if sublevel_id:
                query = query.filter(Soal.sublevel_id == sublevel_id)
            
            # Level filter (via sublevel)
            if level_id:
                query = query.join(SubLevel).filter(SubLevel.level_id == level_id)
            
            # Dictionary filter
            if dictionary_id:
                query = query.filter(Soal.dictionary_id == dictionary_id)
            
            # Sorting
            if hasattr(Soal, sort_by):
                order_func = desc if sort_order.lower() == "desc" else asc
                query = query.order_by(order_func(getattr(Soal, sort_by)))
            
            # ✅ Get ALL data (no limit)
            soal_list = query.all()
            total = len(soal_list)
            
            # Convert ke response format
            soal_data_list = [self._convert_to_list_data(soal) for soal in soal_list]
            
            # Prepare response
            response = {
                "success": True,
                "message": f"Daftar soal berhasil diambil ({total} total)",
                "data": soal_data_list,
                "total": total,
                "filters": {
                    "search": search,
                    "sublevel_id": sublevel_id,
                    "level_id": level_id,
                    "dictionary_id": dictionary_id,
                    "include_deleted": include_deleted,
                    "sort_by": sort_by,
                    "sort_order": sort_order
                },
                "cached": False,
                "cache_ttl_seconds": self._cache_ttl
            }
            
            # ✅ Store to cache
            if use_cache:
                self._set_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal mengambil daftar soal: {str(e)}",
                "data": [],
                "total": 0,
                "filters": None,
                "cached": False
            }
    
    # =====================================================================
    # UPDATE - Update soal
    # =====================================================================
    def update_soal(self, soal_id: int, soal_data: SoalUpdateRequest) -> Dict[str, Any]:
        """Update existing soal"""
        try:
            # Get existing soal (hanya yang tidak di-delete)
            soal = self.db.query(Soal).filter(
                Soal.id == soal_id,
                Soal.deleted_at.is_(None)
            ).first()
            
            if not soal:
                return {
                    "success": False,
                    "message": "Soal tidak ditemukan",
                    "data": None
                }
            
            # Validate foreign keys jika ada perubahan - type-safe
            if soal_data.sublevel_id or soal_data.dictionary_id:
                current_sublevel = self._get_int_value(soal.sublevel_id)
                current_dict = self._get_optional_int(soal.dictionary_id)
                
                new_sublevel_id = soal_data.sublevel_id if soal_data.sublevel_id is not None else current_sublevel
                new_dictionary_id = soal_data.dictionary_id if soal_data.dictionary_id is not None else current_dict
                
                self._validate_foreign_keys(new_sublevel_id, new_dictionary_id)
            
            # Update fields yang disediakan
            if soal_data.pertanyaan is not None:
                setattr(soal, 'question', soal_data.pertanyaan)
            
            if soal_data.jawaban_benar is not None:
                setattr(soal, 'answer', soal_data.jawaban_benar)
            
            if soal_data.video_url is not None:
                setattr(soal, 'video_url', soal_data.video_url)
            
            if soal_data.sublevel_id is not None:
                setattr(soal, 'sublevel_id', soal_data.sublevel_id)
            
            if soal_data.dictionary_id is not None:
                setattr(soal, 'dictionary_id', soal_data.dictionary_id)
            
            # Update timestamp
            setattr(soal, 'updated_at', datetime.now(timezone.utc))
            
            self.db.commit()
            self.db.refresh(soal)
            
            # ✅ Invalidate cache after update
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            # Get updated data
            soal_detail = self._get_soal_detail(soal_id)
                
            return {
                "success": True,
                "message": "Soal berhasil diupdate",
                "data": soal_detail
            }
            
        except ValueError as ve:
            self.db.rollback()
            return {
                "success": False,
                "message": str(ve),
                "data": None
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal mengupdate soal: {str(e)}",
                "data": None
            }
    
    # =====================================================================
    # DELETE - Soft delete soal
    # =====================================================================
    def delete_soal(self, soal_id: int, permanent: bool = False) -> Dict[str, Any]:
        """Delete soal (soft delete by default, permanent jika diminta)"""
        try:
            soal = self.db.query(Soal).filter(Soal.id == soal_id).first()
            
            if not soal:
                return {
                    "success": False,
                    "message": "Soal tidak ditemukan",
                    "data": None
                }
            
            if permanent:
                # Permanent delete
                self.db.delete(soal)
                message = "Soal berhasil dihapus permanen"
                deleted_at = None
            else:
                # Soft delete
                if soal.deleted_at is not None:
                    return {
                        "success": False,
                        "message": "Soal sudah dihapus sebelumnya",
                        "data": None
                    }
                
                setattr(soal, 'deleted_at', datetime.now(timezone.utc))
                message = "Soal berhasil dihapus"
                deleted_at = self._serialize_datetime(soal.deleted_at)
            
            self.db.commit()
            
            # ✅ Invalidate cache after delete
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            return {
                "success": True,
                "message": message,
                "data": {
                    "id": soal_id,
                    "deleted_at": deleted_at,
                    "permanent": permanent
                }
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal menghapus soal: {str(e)}",
                "data": None
            }
    
    def bulk_delete_soal(self, request: BulkDeleteSoalRequest) -> Dict[str, Any]:
        """Bulk delete soal"""
        try:
            soal_list = self.db.query(Soal).filter(Soal.id.in_(request.ids)).all()
            
            if not soal_list:
                return {
                    "success": False,
                    "message": "Tidak ada soal yang ditemukan dengan ID yang diberikan",
                    "data": None
                }
            
            deleted_count = 0
            deleted_ids = []
            
            for soal in soal_list:
                if request.permanent:
                    # Permanent delete
                    self.db.delete(soal)
                    deleted_ids.append(soal.id)
                    deleted_count += 1
                else:
                    # Soft delete (hanya jika belum di-delete)
                    if soal.deleted_at is None:
                        setattr(soal, 'deleted_at', datetime.now(timezone.utc))
                        deleted_ids.append(soal.id)
                        deleted_count += 1
            
            self.db.commit()
            
            # ✅ Invalidate cache after bulk delete
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            return {
                "success": True,
                "message": f"Berhasil menghapus {deleted_count} soal",
                "data": {
                    "deleted_count": deleted_count,
                    "deleted_ids": deleted_ids,
                    "permanent": request.permanent,
                    "total_requested": len(request.ids)
                }
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal bulk delete soal: {str(e)}",
                "data": None
            }
    
    # =====================================================================
    # RESTORE - Restore soft deleted soal
    # =====================================================================
    def restore_soal(self, soal_id: int) -> Dict[str, Any]:
        """Restore soft deleted soal"""
        try:
            soal = self.db.query(Soal).filter(
                Soal.id == soal_id,
                Soal.deleted_at.isnot(None)
            ).first()
            
            if not soal:
                return {
                    "success": False,
                    "message": "Soal yang dihapus tidak ditemukan",
                    "data": None
                }
            
            # Restore soal
            setattr(soal, 'deleted_at', None)
            setattr(soal, 'updated_at', datetime.now(timezone.utc))
            
            self.db.commit()
            self.db.refresh(soal)
            
            # ✅ Invalidate cache after restore
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            # Get restored data
            soal_detail = self._get_soal_detail(soal_id)
            
            return {
                "success": True,
                "message": "Soal berhasil dipulihkan",
                "data": soal_detail
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal memulihkan soal: {str(e)}",
                "data": None
            }
    
    def bulk_restore_soal(self, request: BulkRestoreSoalRequest) -> Dict[str, Any]:
        """Bulk restore soal"""
        try:
            soal_list = self.db.query(Soal).filter(
                Soal.id.in_(request.ids),
                Soal.deleted_at.isnot(None)
            ).all()
            
            if not soal_list:
                return {
                    "success": False,
                    "message": "Tidak ada soal yang dihapus ditemukan dengan ID yang diberikan",
                    "data": None
                }
            
            restored_count = 0
            restored_ids = []
            
            for soal in soal_list:
                setattr(soal, 'deleted_at', None)
                setattr(soal, 'updated_at', datetime.now(timezone.utc))
                restored_ids.append(soal.id)
                restored_count += 1
                
            self.db.commit()
            
            # ✅ Invalidate cache after bulk restore
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            return {
                "success": True,
                "message": f"Berhasil memulihkan {restored_count} soal",
                "data": {
                    "restored_count": restored_count,
                    "restored_ids": restored_ids,
                    "total_requested": len(request.ids)
                }
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal bulk restore soal: {str(e)}",
                "data": None
            }
    
    # =====================================================================
    # HELPER METHODS - Untuk mendukung operasi utama
    # =====================================================================
    def get_available_kamus(self, search: Optional[str] = None) -> Dict[str, Any]:
        """Get available kamus untuk dropdown/selection"""
        try:
            query = self.db.query(Kamus).filter(Kamus.deleted_at.is_(None))
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Kamus.word_text.ilike(search_filter),
                        Kamus.definition.ilike(search_filter)
                    )
                )
            
            kamus_list = query.order_by(Kamus.word_text).all()
            
            kamus_data = [
                {
                    "id": kamus.id,
                    "word_text": kamus.word_text,
                    "definition": kamus.definition,
                    "video_url": kamus.video_url,
                    "total_soal": kamus.total_soal
                }
                for kamus in kamus_list
            ]
            
            return {
                "success": True,
                "message": "Daftar kamus berhasil diambil",
                "data": kamus_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal mengambil daftar kamus: {str(e)}",
                "data": []
            }
    
    def get_available_sublevels(self, level_id: Optional[int] = None) -> Dict[str, Any]:
        """Get available sublevels untuk dropdown/selection"""
        try:
            query = self.db.query(SubLevel).options(
                joinedload(SubLevel.level_ref)
            ).filter(SubLevel.deleted_at.is_(None))
            
            if level_id:
                query = query.filter(SubLevel.level_id == level_id)
            
            sublevel_list = query.order_by(SubLevel.level_id, SubLevel.name).all()
            
            sublevel_data = [
                {
                    "id": sublevel.id,
                    "name": sublevel.name,
                    "description": sublevel.description,
                    "level_id": sublevel.level_id,
                    "level_name": sublevel.level_ref.name if sublevel.level_ref else None,
                    "total_soal": sublevel.total_soal
                }
                for sublevel in sublevel_list
            ]
            
            return {
                "success": True,
                "message": "Daftar sublevel berhasil diambil",
                "data": sublevel_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal mengambil daftar sublevel: {str(e)}",
                "data": []
            }
    
    def get_soal_statistics(self) -> Dict[str, Any]:
        """Get basic statistics untuk dashboard dengan caching"""
        try:
            # ✅ Check cache first
            cache_key = "soal_stats:summary"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
            
            # Basic counts
            total_soal = self.db.query(Soal).count()
            active_soal = self.db.query(Soal).filter(Soal.deleted_at.is_(None)).count()
            deleted_soal = self.db.query(Soal).filter(Soal.deleted_at.isnot(None)).count()
            
            # Count by sublevel
            sublevel_stats = self.db.query(
                SubLevel.id,
                SubLevel.name,
                Level.name.label("level_name"),
                func.count(Soal.id).label("soal_count")
            ).select_from(SubLevel)\
             .join(Level, SubLevel.level_id == Level.id)\
             .outerjoin(Soal, and_(
                 SubLevel.id == Soal.sublevel_id, 
                 Soal.deleted_at.is_(None)
             ))\
             .group_by(SubLevel.id, SubLevel.name, Level.name)\
             .all()
            
            response = {
                "success": True,
                "message": "Statistik berhasil diambil",
                "data": {
                    "summary": {
                        "total_soal": total_soal,
                        "active_soal": active_soal,
                        "deleted_soal": deleted_soal
                    },
                    "by_sublevel": [
                        {
                            "sublevel_id": stat.id,
                            "sublevel_name": stat.name,
                            "level_name": stat.level_name,
                            "soal_count": stat.soal_count
                        }
                        for stat in sublevel_stats
                    ]
                }
            }
            
            # ✅ Store to cache
            self._set_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gagal mengambil statistik: {str(e)}",
                "data": None
            }
    
    # =====================================================================
    # PRIVATE METHODS - Internal helper methods
    # =====================================================================
    def _validate_foreign_keys(self, sublevel_id: int, dictionary_id: Optional[int] = None):
        """Validate foreign key references"""
        # Check sublevel exists
        sublevel = self.db.query(SubLevel).filter(
            SubLevel.id == sublevel_id,
            SubLevel.deleted_at.is_(None)
        ).first()
        
        if not sublevel:
            raise ValueError(f"SubLevel dengan ID {sublevel_id} tidak ditemukan")
        
        # Check dictionary exists jika disediakan
        if dictionary_id:
            kamus = self.db.query(Kamus).filter(
                Kamus.id == dictionary_id,
                Kamus.deleted_at.is_(None)
            ).first()
            
            if not kamus:
                raise ValueError(f"Kamus dengan ID {dictionary_id} tidak ditemukan")
    
    def _get_soal_detail(self, soal_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed soal data dengan relasi"""
        soal = self.db.query(Soal).options(
            joinedload(Soal.kamus_ref),
            joinedload(Soal.sublevel_ref).joinedload(SubLevel.level_ref)
        ).filter(Soal.id == soal_id).first()
        
        if not soal:
            return None
        
        return {
            "id": soal.id,
            "pertanyaan": soal.question,
            "jawaban_benar": soal.answer,
            "video_url": soal.video_url,
            "image_url": soal.image_url,
            "dictionary_id": soal.dictionary_id,
            "sublevel_id": soal.sublevel_id,
            "kamus": {
                "id": soal.kamus_ref.id,
                "word_text": soal.kamus_ref.word_text,
                "definition": soal.kamus_ref.definition,
                "video_url": soal.kamus_ref.video_url
            } if soal.kamus_ref else None,
            "sublevel": {
                "id": soal.sublevel_ref.id,
                "name": soal.sublevel_ref.name,
                "description": soal.sublevel_ref.description,
                "level": {
                    "id": soal.sublevel_ref.level_ref.id,
                    "name": soal.sublevel_ref.level_ref.name
                } if soal.sublevel_ref.level_ref else None
            } if soal.sublevel_ref else None,
            # Convert datetime to ISO string - actual values from committed record
            "created_at": self._serialize_datetime(soal.created_at),
            "updated_at": self._serialize_datetime(soal.updated_at),
            "deleted_at": self._serialize_datetime(soal.deleted_at)
        }
    
    def _convert_to_list_data(self, soal: Soal) -> Dict[str, Any]:
        """✅ Convert soal model ke format list data dengan image_url & video_url"""
        # Extract answer value safely and check length
        answer_value = self._get_str_value(soal.answer)
        truncated_answer = answer_value[:100] + "..." if len(answer_value) > 100 else answer_value
        
        # ✅ Safe extraction untuk image_url & video_url
        image_url_value = self._get_str_value(soal.image_url) if soal.image_url is not None else None
        video_url_value = self._get_str_value(soal.video_url) if soal.video_url is not None else None
        
        return {
            "id": soal.id,
            "pertanyaan": soal.question,
            "jawaban_benar": truncated_answer,
            "dictionary_word": soal.kamus_ref.word_text if soal.kamus_ref else None,
            "sublevel_name": soal.sublevel_ref.name if soal.sublevel_ref else None,
            "level_name": soal.sublevel_ref.level_ref.name if soal.sublevel_ref and soal.sublevel_ref.level_ref else None,
            # ✅ Include actual URLs from database
            "image_url": image_url_value if image_url_value else None,
            "video_url": video_url_value if video_url_value else None,
            # ✅ Keep backward compatibility
            "has_video": bool(video_url_value),
            "has_image": bool(image_url_value),
            # Convert datetime to ISO string - actual values from committed record
            "created_at": self._serialize_datetime(soal.created_at),
            "updated_at": self._serialize_datetime(soal.updated_at),
            "is_deleted": soal.deleted_at is not None
        }
        

    def update_soal_image(self, soal_id: int, image_url: str) -> Dict[str, Any]:
        """Update soal image URL"""
        try:
            soal = self.db.query(Soal).filter(
                Soal.id == soal_id,
                Soal.deleted_at.is_(None)
            ).first()
            
            if not soal:
                return {
                    "success": False,
                    "message": "Soal tidak ditemukan",
                    "data": None
                }
            
            # Update image_url
            setattr(soal, 'image_url', image_url)
            setattr(soal, 'updated_at', datetime.now(timezone.utc))
            
            self.db.commit()
            self.db.refresh(soal)
            
            # ✅ Invalidate cache after update
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            # Get updated data
            soal_detail = self._get_soal_detail(soal_id)
            
            return {
                "success": True,
                "message": "Image URL berhasil diupdate",
                "data": soal_detail
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal update image URL: {str(e)}",
                "data": None
            }
    
    def update_soal_video(self, soal_id: int, video_url: str) -> Dict[str, Any]:
        """Update soal video URL"""
        try:
            soal = self.db.query(Soal).filter(
                Soal.id == soal_id,
                Soal.deleted_at.is_(None)
            ).first()
            
            if not soal:
                return {
                    "success": False,
                    "message": "Soal tidak ditemukan",
                    "data": None
                }
            
            # Update video_url
            setattr(soal, 'video_url', video_url)
            setattr(soal, 'updated_at', datetime.now(timezone.utc))
            
            self.db.commit()
            self.db.refresh(soal)
            
            # ✅ Invalidate cache after update
            self._invalidate_cache("soal_list")
            self._invalidate_cache("soal_stats")
            
            # Get updated data
            soal_detail = self._get_soal_detail(soal_id)
            
            return {
                "success": True,
                "message": "Video URL berhasil diupdate",
                "data": soal_detail
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Gagal update video URL: {str(e)}",
                "data": None
            }