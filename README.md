# CaloriasApp v2

Aplicación multiplataforma para estimar calorías y macronutrientes a partir de fotos de comida.

## Stack
- **UI**: Kivy (Python)
- **Base de datos local**: SQLite
- **Inferencia** (futuro): FastAPI + PyTorch

## Instalación

```bash
pip install -r requirements.txt
python main.py
```

## Estructura del proyecto

```
app-caloriasv2/
├── main.py                  # Punto de entrada
├── app/
│   ├── screens/             # Pantallas de la app
│   │   ├── home.py
│   │   ├── capture.py
│   │   ├── result.py
│   │   └── history.py
│   ├── components/          # Widgets reutilizables
│   │   └── macro_card.py
│   ├── database/            # Capa de persistencia
│   │   └── db.py
│   ├── nutrition/           # Motor nutricional
│   │   └── food_table.py
│   └── services/            # Servicios (inferencia, etc.)
│       └── inference.py
├── assets/
│   ├── fonts/
│   └── images/
└── kv/                      # Archivos de diseño Kivy
    ├── home.kv
    ├── capture.kv
    ├── result.kv
    └── history.kv
```
