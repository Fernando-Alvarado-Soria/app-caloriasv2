"""
Servidor FastAPI para exponer el modelo de clasificación de comida.

Endpoints:
  POST /predict        — Sube imagen, devuelve top-3 predicciones + nutrición
  GET  /health         — Health check
  GET  /classes        — Lista de clases soportadas

Uso local:
    uvicorn server.api:app --reload --port 8000

Producción:
    uvicorn server.api:app --host 0.0.0.0 --port 8000
"""

import os
import io
import json
import logging
import tempfile
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CaloriasApp API",
    description="API de clasificación de comida y estimación de calorías",
    version="1.0.0",
)

# CORS — permitir acceso desde cualquier origen (ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Pre-cargar el modelo al iniciar el servidor."""
    from app.services.inference import _try_load_model, is_model_loaded
    _try_load_model()
    if is_model_loaded():
        logger.info("Modelo cargado correctamente al iniciar.")
    else:
        logger.warning("Modelo NO disponible — las predicciones serán simuladas.")


@app.get("/health")
async def health():
    """Health check endpoint."""
    from app.services.inference import is_model_loaded
    return {
        "status": "ok",
        "model_loaded": is_model_loaded(),
    }


@app.get("/classes")
async def get_classes():
    """Devuelve la lista de clases que el modelo puede reconocer."""
    from ml.class_mapping import CLASS_MAP, food101_to_spanish
    classes = {k: food101_to_spanish(k) for k in CLASS_MAP}
    return {"num_classes": len(classes), "classes": classes}


@app.post("/predict")
async def predict(
    file: UploadFile = File(..., description="Imagen de comida (jpg, png)"),
    portion_grams: float = 100.0,
):
    """
    Clasifica una imagen de comida y devuelve información nutricional.

    - **file**: Imagen de comida (JPEG o PNG)
    - **portion_grams**: Tamaño de la porción en gramos (default: 100)
    """
    # Validar tipo de archivo
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado: {file.content_type}. Usa JPEG o PNG.",
        )

    # Validar tamaño (máx 10 MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Imagen demasiado grande (máx 10 MB).")

    # Validar que sea imagen válida
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida.")

    # Guardar temporalmente para inferencia
    tmp_dir = tempfile.mkdtemp()
    try:
        suffix = ".jpg" if "jpeg" in (file.content_type or "") or "jpg" in (file.content_type or "") else ".png"
        tmp_path = os.path.join(tmp_dir, f"upload{suffix}")
        with open(tmp_path, "wb") as f:
            f.write(contents)

        # Ejecutar predicción
        from app.services.inference import predict_food, is_model_loaded
        predictions = predict_food(tmp_path)

        # Agregar información nutricional
        from app.nutrition.food_table import estimate_nutrition
        results = []
        for pred in predictions:
            nutrition = estimate_nutrition(pred["food_class"], grams=portion_grams)
            results.append({
                **pred,
                "portion_grams": portion_grams,
                "nutrition": nutrition,
            })

        return {
            "model_loaded": is_model_loaded(),
            "predictions": results,
        }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
