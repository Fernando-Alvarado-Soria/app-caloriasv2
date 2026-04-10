"""
Descarga imágenes para clases personalizadas (comida mexicana)
usando DuckDuckGo Search (no requiere API key).

Uso:
    python -m ml.collect_images
    python -m ml.collect_images --classes "sopes,tamales,pozole"
    python -m ml.collect_images --per-class 150
"""

import os
import time
import hashlib
import argparse
import requests
from pathlib import Path

# ─── Clases de comida mexicana a agregar ───
MEXICAN_CLASSES = {
    "caldo_de_pollo":       "caldo de pollo mexicano comida",
    "tacos_dorados":        "tacos dorados mexicanos comida",
    "sopes":                "sopes mexicanos comida",
    "tamales":              "tamales mexicanos comida",
    "pozole":               "pozole rojo mexicano comida",
    "chilaquiles":          "chilaquiles rojos verdes comida mexicana",
    "gorditas":             "gorditas mexicanas comida",
    "tlacoyos":             "tlacoyos mexicanos comida",
    "elote":                "elote mexicano esquites comida",
    "torta_mexicana":       "torta mexicana comida",
    "molletes":             "molletes mexicanos comida",
    "huevos_rancheros":     "huevos rancheros comida mexicana",
    "arroz_rojo":           "arroz rojo mexicano comida",
    "frijoles":             "frijoles refritos mexicanos comida",
    "carne_en_su_jugo":     "carne en su jugo comida mexicana",
    "birria":               "birria de res comida mexicana",
    "menudo":               "menudo rojo comida mexicana",
    "flautas":              "flautas mexicanas comida",
    "mole":                 "mole poblano comida mexicana",
    "chiles_rellenos":      "chiles rellenos comida mexicana",
}

IMAGES_PER_CLASS = 150  # mínimo recomendado para fine-tuning
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mexican_food")


def download_images_ddg(query: str, max_images: int, output_dir: str):
    """Descarga imágenes usando DuckDuckGo (sin API key)."""
    from duckduckgo_search import DDGS

    os.makedirs(output_dir, exist_ok=True)
    existing = len([f for f in os.listdir(output_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])

    if existing >= max_images:
        print(f"  Ya tiene {existing} imágenes, saltando.")
        return existing

    needed = max_images - existing
    print(f"  Descargando {needed} imágenes (ya hay {existing})...")

    downloaded = 0
    try:
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=needed + 50)  # extras por si fallan
            for r in results:
                if downloaded >= needed:
                    break
                url = r.get("image", "")
                if not url:
                    continue
                try:
                    resp = requests.get(url, timeout=10, stream=True)
                    if resp.status_code != 200:
                        continue
                    content_type = resp.headers.get("content-type", "")
                    if "image" not in content_type:
                        continue

                    # Nombre único basado en hash del URL
                    ext = ".jpg"
                    if "png" in content_type:
                        ext = ".png"
                    fname = hashlib.md5(url.encode()).hexdigest()[:12] + ext
                    fpath = os.path.join(output_dir, fname)

                    if os.path.exists(fpath):
                        continue

                    with open(fpath, "wb") as f:
                        for chunk in resp.iter_content(8192):
                            f.write(chunk)

                    # Verificar que es imagen válida
                    from PIL import Image
                    img = Image.open(fpath)
                    img.verify()

                    downloaded += 1
                    if downloaded % 20 == 0:
                        print(f"    {downloaded}/{needed}")

                except Exception:
                    # Eliminar archivo corrupto
                    if os.path.exists(fpath):
                        os.remove(fpath)
                    continue

                time.sleep(0.2)  # Rate limiting

    except Exception as e:
        print(f"  Error en búsqueda: {e}")

    total = existing + downloaded
    print(f"  Total: {total} imágenes")
    return total


def collect_all(classes: dict = None, per_class: int = IMAGES_PER_CLASS):
    """Descarga imágenes para todas las clases mexicanas."""
    if classes is None:
        classes = MEXICAN_CLASSES

    print(f"Recolectando imágenes para {len(classes)} clases mexicanas")
    print(f"Imágenes por clase: {per_class}")
    print(f"Directorio: {DATA_DIR}")
    print()

    stats = {}
    for class_name, search_query in classes.items():
        print(f"[{class_name}] buscando: '{search_query}'")
        output_dir = os.path.join(DATA_DIR, class_name)
        count = download_images_ddg(search_query, per_class, output_dir)
        stats[class_name] = count
        print()

    # Resumen
    print("=" * 50)
    print("RESUMEN DE RECOLECCIÓN")
    print("=" * 50)
    for cls, count in stats.items():
        status = "✓" if count >= per_class * 0.7 else "⚠ POCAS"
        print(f"  {cls:<25} {count:>4} imágenes  {status}")

    total = sum(stats.values())
    print(f"\nTotal: {total} imágenes en {len(stats)} clases")
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recolectar imágenes de comida mexicana")
    parser.add_argument("--classes", type=str, default=None,
                        help="Clases a descargar separadas por coma (default: todas)")
    parser.add_argument("--per-class", type=int, default=IMAGES_PER_CLASS,
                        help="Imágenes por clase")
    args = parser.parse_args()

    if args.classes:
        selected = {k: v for k, v in MEXICAN_CLASSES.items()
                    if k in args.classes.split(",")}
    else:
        selected = MEXICAN_CLASSES

    collect_all(selected, args.per_class)
