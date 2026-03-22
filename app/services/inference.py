"""
Servicio de inferencia simulado.

En la Fase 1 devuelve una predicción aleatoria de las clases disponibles.
Cuando el modelo esté entrenado, este módulo se conectará al backend FastAPI
o cargará el modelo localmente.
"""

import random
from app.nutrition.food_table import get_food_classes


def predict_food(image_path: str) -> list[dict]:
    """
    Simula la predicción del modelo.
    Devuelve top-3 clases con confianza simulada.

    En producción esto hará:
      1. Enviar imagen al backend FastAPI, o
      2. Cargar modelo local y ejecutar inferencia.
    """
    classes = get_food_classes()
    top3 = random.sample(classes, min(3, len(classes)))

    confidences = sorted(
        [random.uniform(0.3, 0.95) for _ in top3], reverse=True
    )

    results = []
    for cls, conf in zip(top3, confidences):
        results.append({
            "food_class": cls,
            "confidence": round(conf, 2),
        })

    return results
