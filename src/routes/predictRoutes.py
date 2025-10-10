from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import base64
import io
from PIL import Image
import numpy as np
from typing import Optional
import os

# ✅ PUBLIC ROUTER - No authentication dependencies
router = APIRouter(
    prefix="/predict",
    tags=["ML Prediction - Public"]
    # ❌ NO dependencies=[Depends(require_user)] - This makes it PUBLIC
)

# ✅ Global variable untuk cache model
_model = None
_model_path = "ml/mauna.h5"

def get_model():
    """Lazy load model - only load when needed"""
    global _model
    
    if _model is None:
        try:
            # Suppress TensorFlow warnings
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
            os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
            
            from tensorflow.keras.models import load_model
            
            if not os.path.exists(_model_path):
                raise FileNotFoundError(f"Model file not found: {_model_path}")
            
            print(f"🔄 Loading ML model from {_model_path}...")
            _model = load_model(_model_path)
            print(f"✅ ML model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load ML model: {str(e)}"
            )
    
    return _model

class ImageData(BaseModel):
    """Image data for prediction"""
    image: str  # Base64 encoded image

class PredictionResponse(BaseModel):
    """Prediction response"""
    success: bool
    message: str
    data: dict

@router.post("/", response_model=PredictionResponse)
async def predict_image(data: ImageData) -> dict:
    """
    🌍 PUBLIC ENDPOINT - No authentication required
    
    Predict sign language gesture from base64 encoded image
    
    **Request Body:**
    - image: Base64 encoded image string (with or without data URI prefix)
    
    **Response:**
    - success: Boolean indicating success
    - message: Success/error message
    - data: Prediction results (class, label, confidence)
    
    **Example:**
    ```json
    {
        "image": "data:image/png;base64,iVBORw0KGgo..."
    }
    ```
    """
    try:
        model = get_model()
        
        # ✅ Safely decode base64 with error handling
        try:
            if "," in data.image:
                img_data = base64.b64decode(data.image.split(",")[1])
            else:
                img_data = base64.b64decode(data.image)
        except Exception as decode_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid base64 image: {str(decode_error)}"
            )
        
        # Process image
        try:
            image = Image.open(io.BytesIO(img_data)).convert("RGB")
            image = image.resize((224, 224))
            img_array = np.array(image) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
        except Exception as img_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image format: {str(img_error)}"
            )

        # Predict
        try:
            prediction = model.predict(img_array, verbose=0)
            class_idx = int(np.argmax(prediction))
            confidence = float(np.max(prediction))
        except Exception as pred_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prediction failed: {str(pred_error)}"
            )
        
        class_labels = _get_class_labels()
        label = class_labels.get(class_idx, f"Class_{class_idx}")
        
        return {
            "success": True,
            "message": "Prediction successful",
            "data": {
                "class": class_idx,
                "class_label": label,
                "confidence": confidence,
                "confidence_percentage": round(confidence * 100, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )

def _get_class_labels() -> dict:
    """
    Get class label mapping
    Update this based on your model's classes
    """
    # ✅ TODO: Update dengan class labels sebenarnya dari model
    return {
        0: "A",
        1: "B",
        2: "C",
        3: "D",
        4: "E",
        # ... add more mappings based on your model
    }

@router.get("/health")
async def health_check() -> dict:
    """
    🌍 PUBLIC ENDPOINT - Check if ML model is loaded and ready
    """
    try:
        model = get_model()
        return {
            "success": True,
            "message": "ML model is ready",
            "model_loaded": model is not None,
            "model_path": _model_path
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"ML model not loaded: {str(e)}",
            "model_loaded": False
        }

@router.get("/classes")
async def get_classes() -> dict:
    """
    🌍 PUBLIC ENDPOINT - Get list of available classes
    """
    return {
        "success": True,
        "message": "Available classes",
        "data": {
            "classes": _get_class_labels(),
            "total_classes": len(_get_class_labels())
        }
    }