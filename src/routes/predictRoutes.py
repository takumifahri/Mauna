# src/routes/predictRoutes.py

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.models import load_model, Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, GlobalMaxPooling2D, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
import numpy as np
from PIL import Image
import io
import cv2
import mediapipe as mp
import os
import traceback

# Inisialisasi router
router = APIRouter(
    prefix="/predict",
    tags=["ML Prediction"],
    responses={
        503: {"description": "Service Unavailable - Model not loaded"}
    }
)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Global variables
model = None
labels_list = None

# ✅ PERBAIKAN: Gunakan arsitektur yang dikoreksi
def build_model(num_classes=24):
    """
    Rebuild the exact model architecture for debugging/h5 weights.
    This version correctly uses the Keras Functional API.
    """
    base_model = MobileNet(
        include_top=False, 
        weights='imagenet', 
        input_shape=(224, 224, 3)
    )
    for layer in base_model.layers:
        layer.trainable = False
    for layer in base_model.layers[-80:]:
        layer.trainable = True

    model_output = base_model.output
    model_output = GlobalMaxPooling2D()(model_output)
    model_output = BatchNormalization()(model_output)
    model_output = Dense(1024, activation='relu')(model_output)
    model_output = Dropout(0.3)(model_output)
    model_output = BatchNormalization()(model_output)
    model_output = Dense(512, activation='relu')(model_output)
    final_output = Dense(num_classes, activation='softmax')(model_output)

    return Model(inputs=base_model.input, outputs=final_output)

def load_model_safe():
    """
    Safely loads the entire model from the .keras file.
    This is the most reliable way as the .keras format saves the full model.
    """
    global model, labels_list
    
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ml_dir = os.path.join(base_dir, '..', 'ml')

        model_path = os.path.join(ml_dir, 'mauna.keras')
        labels_path = os.path.join(ml_dir, 'labels_list.npy')
        
        print(f"DEBUG: Checking for model at: {model_path}")
        print(f"DEBUG: Checking for labels at: {labels_path}")

        if not os.path.exists(model_path):
            print(f"ERROR: Model file not found at {model_path}")
            return False
        if not os.path.exists(labels_path):
            print(f"ERROR: Labels file not found at {labels_path}")
            return False

        print("Loading labels...")
        labels_list = np.load(labels_path, allow_pickle=True)
        print(f"✓ Labels loaded: {len(labels_list)} classes")
        
        print(f"Loading entire model from {model_path}...")
        
        # ✅ TRY-CATCH KHUSUS UNTUK LOAD MODEL
        try:
            # Perhatikan: jika model dibuat dengan Sequential API, ini akan berhasil.
            # Jika dibuat dengan Functional API, ini mungkin akan gagal.
            model = load_model(model_path)
            print("✓ Model loaded successfully!")
        except Exception as e:
            print(f"FATAL ERROR: Failed to load model with `load_model()`. Trying manual rebuild.")
            # Fallback ke rebuild arsitektur dan load weights jika load_model gagal
            try:
                # Ini mengasumsikan modelmu memiliki 24 kelas
                num_classes = len(labels_list) if labels_list is not None else 24
                # ✅ PANGGIL FUNGSI YANG DIKOREKSI
                model = build_model(num_classes)
                model.load_weights(model_path)
                model.compile(
                    optimizer=Adam(learning_rate=1e-4),
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                print("✓ Model loaded successfully via manual rebuild!")
            except Exception as e2:
                print(f"FATAL ERROR: Manual rebuild also failed. Error: {e2}")
                raise e2
        
        return True
    except Exception as e:
        print("\n" + "="*50)
        print("FATAL ERROR: Failed to load ML model in general.")
        print(f"Detail: {e}")
        print("="*50 + "\n")
        traceback.print_exc()
        return False
        
def extract_hand_crop(frame):
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        x_min, y_min = w, h
        x_max, y_max = 0, 0
        for landmark in hand_landmarks.landmark:
            x, y = int(landmark.x * w), int(landmark.y * h)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x)
            y_max = max(y_max, y)
        pad = 40
        x_min = max(0, x_min - pad)
        y_min = max(0, y_min - pad)
        x_max = min(w, x_max + pad)
        y_max = min(h, y_max + pad)
        crop = frame[y_min:y_max, x_min:x_max]
        return crop, (x_min, y_min, x_max, y_max), hand_landmarks
    return None, None, None

def preprocess_hand(crop):
    if crop is None or crop.size == 0:
        return None
    resized = cv2.resize(crop, (224, 224))
    processed = preprocess_input(np.expand_dims(resized, axis=0))
    return processed

def get_model():
    if model is None or labels_list is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is still loading or failed to load during startup."
        )
    return model, labels_list

@router.post("/")
async def predict_gesture(
    file: UploadFile = File(..., description="Image file (JPG, PNG, etc.)"),
    model_data: tuple = Depends(get_model)
):
    model, labels_list = model_data
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Please upload an image file."
        )
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_array = np.array(image)
        frame = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        crop, bbox, landmarks = extract_hand_crop(frame)
        
        if crop is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hand detected in image. Please make sure your hand is clearly visible in the image."
            )
        batch = preprocess_hand(crop)
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to preprocess image."
            )
        predictions = model.predict(batch, verbose=0)
        predicted_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_index])
        predicted_label = str(labels_list[predicted_index])
        top_3_idx = np.argsort(predictions[0])[-3:][::-1]
        top_3_predictions = {
            str(labels_list[idx]): float(predictions[0][idx])
            for idx in top_3_idx
        }
        return {
            "predicted_label": predicted_label,
            "confidence": confidence,
            "top_3_predictions": top_3_predictions,
            "hand_detected": True,
            "bounding_box": {
                "x_min": int(bbox[0]),
                "y_min": int(bbox[1]),
                "x_max": int(bbox[2]),
                "y_max": int(bbox[3])
            } if bbox else None
        }
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Prediction error: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}",
        )