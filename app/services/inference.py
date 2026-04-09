"""
Servicio de inferencia.

Estrategia de predicción (en orden de prioridad):
  1. API en la nube (Railway) — no necesita modelo local
  2. Modelo local (TorchScript) — si existe en ml/models/export/
  3. Modo simulado (aleatorio) — fallback de último recurso
"""

import os
import json
import random
import logging

import requests
from PIL import Image

logger = logging.getLogger(__name__)

# ─── Configuración de la API en la nube ───
API_URL = os.environ.get(
    "API_URL",
    "https://app-caloriasv2-production.up.railway.app",
)
API_TIMEOUT = 15  # segundos

# ─── Rutas del modelo exportado (local) ───
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_EXPORT_DIR = os.path.join(_ROOT, "ml", "models", "export")
_SCRIPTED_PATH = os.path.join(_EXPORT_DIR, "model_scripted.pt")
_META_PATH = os.path.join(_EXPORT_DIR, "metadata.json")

# Estado global del modelo local (singleton lazy)
_model = None
_classes = None
_transform = None
_device = None
_model_loaded = False
_load_attempted = False

# Estado de la API en la nube
_api_available = None  # None = no probado, True/False


def _try_load_model():
    """Intenta cargar el modelo una sola vez."""
    global _model, _classes, _transform, _device, _model_loaded, _load_attempted

    if _load_attempted:
        return _model_loaded
    _load_attempted = True

    try:
        import torch
        from torchvision import transforms

        if not os.path.exists(_SCRIPTED_PATH):
            logger.info("Modelo no encontrado en %s — modo simulado", _SCRIPTED_PATH)
            return False

        # Cargar metadata
        with open(_META_PATH, "r") as f:
            meta = json.load(f)

        _classes = meta["classes"]
        img_size = meta.get("image_size", 224)
        norm_mean = meta["normalize"]["mean"]
        norm_std = meta["normalize"]["std"]

        # Transform de inferencia
        _transform = transforms.Compose([
            transforms.Resize(img_size + 32),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=norm_mean, std=norm_std),
        ])

        # Cargar modelo
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _model = torch.jit.load(_SCRIPTED_PATH, map_location=_device)
        _model.eval()

        _model_loaded = True
        logger.info("Modelo cargado correctamente (%d clases, device=%s)",
                     len(_classes), _device)
        return True

    except Exception as e:
        logger.warning("Error cargando modelo: %s — modo simulado", e)
        return False


def _check_api():
    """Verifica si la API en la nube está disponible."""
    global _api_available
    if _api_available is not None:
        return _api_available
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        _api_available = resp.status_code == 200
        if _api_available:
            logger.info("API en la nube disponible: %s", API_URL)
        return _api_available
    except Exception:
        _api_available = False
        logger.info("API en la nube no disponible — usando modo local")
        return False


def _predict_cloud(image_path: str) -> list[dict] | None:
    """Envía la imagen a la API en Railway y devuelve predicciones."""
    try:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
            resp = requests.post(
                f"{API_URL}/predict",
                files=files,
                timeout=API_TIMEOUT,
            )

        if resp.status_code != 200:
            logger.warning("API respondió con status %d", resp.status_code)
            return None

        data = resp.json()
        return data.get("predictions", None)

    except Exception as e:
        logger.warning("Error conectando con la API: %s", e)
        return None


def predict_food(image_path: str) -> list[dict]:
    """
    Predice la clase de comida en la imagen.
    Devuelve top-3 clases con confianza.

    Orden de prioridad:
      1. API en la nube (Railway)
      2. Modelo local (TorchScript)
      3. Modo simulado (aleatorio)
    """
    # 1. Intentar API en la nube
    if _check_api():
        result = _predict_cloud(image_path)
        if result:
            return result

    # 2. Intentar modelo local
    if _try_load_model():
        return _predict_real(image_path)

    # 3. Fallback simulado
    return _predict_simulated()


def _predict_real(image_path: str) -> list[dict]:
    """Inferencia real con el modelo entrenado."""
    import torch

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        logger.error("No se pudo abrir la imagen: %s", e)
        return _predict_simulated()

    input_tensor = _transform(img).unsqueeze(0).to(_device)

    with torch.no_grad():
        output = _model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)

    # Top-3
    top3_prob, top3_idx = torch.topk(probabilities, 3)

    # Convertir a nombres con mapeo español
    from ml.class_mapping import food101_to_spanish, food101_to_food_table_key

    results = []
    for prob, idx in zip(top3_prob, top3_idx):
        class_name = _classes[idx.item()]
        food_table_key = food101_to_food_table_key(class_name)
        spanish_name = food101_to_spanish(class_name)

        results.append({
            "food_class": food_table_key or class_name.replace("_", " "),
            "display_name": spanish_name,
            "original_class": class_name,
            "confidence": round(prob.item(), 3),
        })

    return results


def _predict_simulated() -> list[dict]:
    """Fallback: predicción aleatoria cuando no hay modelo."""
    from app.nutrition.food_table import get_food_classes

    classes = get_food_classes()
    top3 = random.sample(classes, min(3, len(classes)))

    confidences = sorted(
        [random.uniform(0.3, 0.95) for _ in top3], reverse=True
    )

    results = []
    for cls, conf in zip(top3, confidences):
        results.append({
            "food_class": cls,
            "display_name": cls.title(),
            "original_class": cls,
            "confidence": round(conf, 2),
        })

    return results


def is_model_loaded() -> bool:
    """Devuelve si hay un modelo disponible (nube o local)."""
    if _check_api():
        return True
    _try_load_model()
    return _model_loaded


def get_inference_mode() -> str:
    """Devuelve el modo actual: 'nube', 'local' o 'simulado'."""
    if _check_api():
        return "nube"
    if _try_load_model():
        return "local"
    return "simulado"
