from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from src.utils.FileHandler import save_image
from src.models.kamus import kamus
import os
class KamusHandler:
    def __init__(self, db: Session):
        self.db = db

    def create_kamus(self, word_text: str, definition: str, image: Optional[UploadFile] = None, video_url: Optional[str] = None) -> Dict[str, Any]:
        print(f"🔍 Handler Debug: word_text={word_text}, definition={definition}")
        print(f"🔍 Handler Debug: image={image}, video_url={video_url}")
        
        # Check for existing word
        if self.db.query(kamus).filter(kamus.word_text == word_text).first():
            raise HTTPException(status_code=400, detail="Word already exists")
        
        # Handle image upload
        image_url_ref = None
        if image and image.filename:
            print("📤 Processing image upload...")
            try:
                image_url_ref = save_image(image, "kamus")
                print(f"✅ Image saved with path: {image_url_ref}")
            except Exception as e:
                print(f"❌ Image upload failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
        else:
            print("ℹ️ No image provided")
        
        # Create new entry
        new_entry = kamus(
            word_text=word_text,
            definition=definition,
            image_url_ref=image_url_ref,
            video_url=video_url
        )
        
        try:
            self.db.add(new_entry)
            self.db.commit()
            self.db.refresh(new_entry)
            print(f"✅ Kamus entry created with ID: {new_entry.id}")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return {
            "success": True,
            "data": {
                "id": new_entry.id,
                "word_text": new_entry.word_text,
                "definition": new_entry.definition,
                "image_url_ref": new_entry.image_url_ref,
                "video_url": new_entry.video_url,
                "created_at": new_entry.created_at,
                "updated_at": new_entry.updated_at
            }
        }

    def update_kamus(self, kamus_id: int, word_text: Optional[str] = None, definition: Optional[str] = None, image: Optional[UploadFile] = None, video_url: Optional[str] = None) -> Dict[str, Any]:
        item = self.db.query(kamus).filter(kamus.id == kamus_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Kamus not found")
        
        # Update fields if provided
        if not item:
            raise HTTPException(status_code=404, detail="Kamus not found")
        if not item:
            raise HTTPException(status_code=404, detail="Kamus not found")
        if word_text:
            setattr(item, "word_text", word_text)
        if definition:
            setattr(item, "definition", definition)
        if video_url:
            setattr(item, "video_url", video_url)
        self.db.commit()
        self.db.refresh(item)
        # Handle image update
        if image and image.filename:
            try:
                new_image_path = save_image(image, "kamus")
                setattr(item, "image_url_ref", new_image_path)
                print(f"✅ Image updated with path: {new_image_path}")
            except Exception as e:
                print(f"❌ Image update failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Image update failed: {str(e)}")
        
        try:
            self.db.commit()
            self.db.refresh(item)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return {
            "success": True,
            "data": {
                "id": item.id,
                "word_text": item.word_text,
                "definition": item.definition,
                "image_url_ref": item.image_url_ref,
                "video_url": item.video_url,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            }
        }

    def get_kamus(self, kamus_id: int) -> Dict[str, Any]:
        item = self.db.query(kamus).filter(kamus.id == kamus_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Kamus not found")
        return {
            "success": True,
            "data": {
                "id": item.id,
                "word_text": item.word_text,
                "definition": item.definition,
                "image_url_ref": item.image_url_ref,
                "video_url": item.video_url,
                "created_at": item.created_at,
                "updated_at": item.updated_at
            }
        }

    def list_kamus(self, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        items = self.db.query(kamus).offset(skip).limit(limit).all()
        return {
            "success": True,
            "data": [
                {
                    "id": k.id,
                    "word_text": k.word_text,
                    "definition": k.definition,
                    "image_url_ref": k.image_url_ref,
                    "video_url": k.video_url,
                    "created_at": k.created_at,
                    "updated_at": k.updated_at
                } for k in items
            ]
        }

    def delete_kamus(self, kamus_id: int) -> Dict[str, Any]:
        item = self.db.query(kamus).filter(kamus.id == kamus_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Kamus not found")
        
        # # Optional: Delete associated image file
        # if item.image_url_ref:
        #     try:
        #         file_path = os.path.join(os.path.dirname(__file__), "..", "..", str(item.image_url_ref))
        #         if os.path.exists(file_path):
        #             os.remove(file_path)
        #             print(f"🗑️ Deleted image file: {file_path}")
        #     except Exception as e:
        #         print(f"⚠️ Could not delete image file: {e}")
        
        self.db.delete(item)
        self.db.commit()
        return {
            "success": True,
            "message": f"Kamus id {kamus_id} deleted"
        }