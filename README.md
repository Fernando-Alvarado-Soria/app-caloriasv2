# CaloriasApp v2

Aplicación multiplataforma para estimar calorías y macronutrientes a partir de fotos de comida.  
Usa **Kivy** como interfaz, **EfficientNet-B0** (transfer learning con Food-101) para reconocer comidas, y una tabla nutricional basada en USDA para calcular macros.

## Stack

- **UI**: Python + Kivy 2.3
- **ML**: PyTorch + torchvision (EfficientNet-B0, transfer learning)
- **Base de datos**: SQLite (local)
- **Dataset**: [Food-101](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) (101 clases, 101k imágenes)
- **Escalado futuro**: FastAPI + PostgreSQL

---

## Requisitos previos

- Python 3.11 o superior
- pip
- Git
- Conexión a internet (para descargar dataset y pesos del modelo)
- ~6 GB de espacio libre (dataset + modelo)

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/Fernando-Alvarado-Soria/app-caloriasv2.git
cd app-caloriasv2
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

**Windows PowerShell** (requiere `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`):
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la app (modo simulado)

```bash
python main.py
```

La app funciona sin modelo entrenado. Las predicciones serán aleatorias (modo **[Simulado]**) pero toda la interfaz es funcional: puedes seleccionar imágenes, elegir porciones, guardar comidas y ver el historial.

### 5. Entrenar el modelo de IA

Para que la app reconozca comidas reales, necesitas entrenar el modelo. Ejecuta estos comandos en orden:

```bash
# Paso 1: Descargar dataset Food-101 (~5 GB, solo la primera vez)
python -m ml.download_dataset

# Paso 2: Entrenar el modelo (5-10 épocas recomendadas)
python -m ml.train --epochs 5

# Paso 3: Exportar el modelo para la app
python -m ml.export_model

# Paso 4 (opcional): Evaluar precisión del modelo
python -m ml.evaluate
```

O todo en un solo comando:
```bash
python -m ml.run_pipeline --epochs 5
```

> **Nota sobre rendimiento:** El entrenamiento en CPU puede tardar varias horas por época. Si tienes GPU NVIDIA con CUDA, instala la versión CUDA de PyTorch para acelerar significativamente:
> ```bash
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
> ```

### 6. Ejecutar la app con IA real

```bash
python main.py
```

Ahora verás **[IA]** en la pantalla de resultado y las predicciones serán reales, con nombres en español.

---

## Cómo funciona

1. El usuario toma o selecciona una foto de comida
2. El modelo (EfficientNet-B0) clasifica la comida y devuelve las 3 opciones más probables
3. El usuario confirma o corrige la predicción
4. El usuario elige tamaño de porción (pequeña / mediana / grande) o ingresa gramos exactos
5. La app calcula calorías, proteína, carbohidratos y grasa usando valores USDA
6. El resultado se guarda en el historial local (SQLite)

---

## Estructura del proyecto

```
app-caloriasv2/
├── main.py                      # Punto de entrada de la app
│
├── app/                         # Código de la aplicación Kivy
│   ├── screens/                 # Pantallas
│   │   ├── home.py              #   Resumen diario de calorías y macros
│   │   ├── capture.py           #   Captura/selección de imagen
│   │   ├── result.py            #   Resultado con predicción y nutrición
│   │   └── history.py           #   Historial de comidas
│   ├── components/              # Widgets reutilizables
│   │   └── macro_card.py        #   Tarjeta de macronutriente
│   ├── database/                # Persistencia
│   │   └── db.py                #   CRUD SQLite
│   ├── nutrition/               # Motor nutricional
│   │   └── food_table.py        #   Tabla USDA + cálculo de macros
│   └── services/                # Servicios
│       └── inference.py         #   Carga modelo real o cae en simulado
│
├── kv/                          # Archivos de diseño Kivy (.kv)
│   ├── home.kv
│   ├── capture.kv
│   ├── result.kv
│   └── history.kv
│
├── ml/                          # Pipeline de Machine Learning
│   ├── config.py                #   Hiperparámetros y rutas
│   ├── download_dataset.py      #   Descarga Food-101
│   ├── class_mapping.py         #   Mapeo inglés → español + tabla nutricional
│   ├── train.py                 #   Entrenamiento con transfer learning
│   ├── evaluate.py              #   Evaluación detallada del modelo
│   ├── export_model.py          #   Exportación a TorchScript
│   └── run_pipeline.py          #   Pipeline completo en un comando
│
├── requirements.txt
├── .gitignore
└── README.md
```

### Archivos generados (no incluidos en git)

| Carpeta | Contenido | Tamaño aprox. |
|---------|-----------|---------------|
| `ml/data/` | Dataset Food-101 (imágenes) | ~5 GB |
| `ml/models/best_model.pt` | Mejor modelo entrenado | ~17 MB |
| `ml/models/export/` | Modelo TorchScript + metadata | ~17 MB |
| `data/` | Base de datos SQLite del usuario | Variable |
| `.venv/` | Entorno virtual Python | Variable |

---

## Estrategia de ML

- **Modelo base:** EfficientNet-B0 preentrenado en ImageNet
- **Transfer learning:** Se reemplaza la cabeza de clasificación (1000 → 101 clases)
- **Entrenamiento en 2 fases:**
  - Épocas 1-3: backbone congelado, solo entrena el clasificador
  - Épocas 4+: backbone descongelado, fine-tuning completo con LR diferenciado
- **Exportación:** TorchScript para inferencia optimizada
- **Estimación nutricional:** Clasificación + porción manual (Estrategia A)

---

## Contribuir

1. Haz fork del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/mi-mejora`
3. Haz commit de tus cambios: `git commit -m "Agrega mi mejora"`
4. Push a tu rama: `git push origin feature/mi-mejora`
5. Abre un Pull Request

---

## Roadmap

- [x] App cliente Kivy (4 pantallas funcionales)
- [x] Base de datos local SQLite
- [x] Tabla nutricional con ~35 comidas
- [x] Pipeline ML: descarga, entrenamiento, evaluación, exportación
- [x] Integración modelo real en la app
- [ ] Mejorar motor de calorías (más clases, porciones inteligentes)
- [ ] Backend FastAPI para servir el modelo
- [ ] Autenticación de usuarios
- [ ] PostgreSQL para datos en la nube
- [ ] Empaquetado para Android (Buildozer)

---

## Licencia

Este proyecto es de código abierto.
