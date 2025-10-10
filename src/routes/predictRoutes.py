from fastapi import APIRouter
from pydantic import BaseModel
import base64
import io
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

router = APIRouter()

model = load_model("ml/mauna.h5")

class ImageData(BaseModel):
    image: str


@router.post("/predict")
async def predict(data: ImageData):
    img_data = base64.b64decode(data.image.split(",")[1])
    image = Image.open(io.BytesIO(img_data)).convert("RGB")
    image = image.resize((224, 224))  # sesuaikan ukuran input model
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    class_idx = int(np.argmax(prediction))
    confidence = float(np.max(prediction))

    return {
        "class": class_idx,
        "confidence": confidence
    }
