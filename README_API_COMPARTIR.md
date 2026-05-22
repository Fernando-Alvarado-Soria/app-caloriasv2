# Guia corta para consumir la API de CaloriasApp

Esta guia es para desarrolladores que quieran usar el modelo entrenado desde otra app (Kivy, Flutter, React, backend, etc.).

## Base URL

https://app-caloriasv2-production.up.railway.app

## Endpoints

### 1) Health check

GET /health

Ejemplo:

```bash
curl https://app-caloriasv2-production.up.railway.app/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### 2) Lista de clases

GET /classes

Ejemplo:

```bash
curl https://app-caloriasv2-production.up.railway.app/classes
```

### 3) Prediccion por imagen

POST /predict

Content-Type: multipart/form-data

Campos:
- file: imagen .jpg o .png (obligatorio)
- portion_grams: gramos de porcion (opcional, default 100)

Ejemplo con curl:

```bash
curl -X POST "https://app-caloriasv2-production.up.railway.app/predict" \
  -F "file=@mi_foto.jpg" \
  -F "portion_grams=150"
```

Ejemplo con Python:

```python
import requests

url = "https://app-caloriasv2-production.up.railway.app/predict"

with open("mi_foto.jpg", "rb") as f:
    res = requests.post(
        url,
        files={"file": ("mi_foto.jpg", f, "image/jpeg")},
        data={"portion_grams": 150},
        timeout=20,
    )

print(res.status_code)
print(res.json())
```

Respuesta (formato):

```json
{
  "model_loaded": true,
  "predictions": [
    {
      "food_class": "sushi",
      "display_name": "Sushi",
      "original_class": "sushi",
      "confidence": 0.913,
      "portion_grams": 150,
      "nutrition": {
        "calories": 210,
        "protein": 8.2,
        "carbs": 28.0,
        "fat": 6.0
      }
    }
  ]
}
```

## Recomendaciones para uso real

- Validar siempre /health antes de enviar imagenes.
- Si van a usar frontend web, considerar restringir CORS por dominio.
- Si la API sera publica, agregar API key y rate limit.
- Para pruebas rapidas, abrir la documentacion interactiva en:
  https://app-caloriasv2-production.up.railway.app/docs
