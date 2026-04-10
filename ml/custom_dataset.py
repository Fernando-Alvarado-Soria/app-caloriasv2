"""
Dataset combinado: Food-101 + clases mexicanas personalizadas.

Carga Food-101 de torchvision y agrega carpetas con imágenes propias.
Divide las imágenes propias en train (80%) y test (20%).
"""

import os
import random
from pathlib import Path

from PIL import Image
from torch.utils.data import Dataset
from torchvision.datasets import Food101

from ml.collect_images import MEXICAN_CLASSES, DATA_DIR as MEXICAN_DIR


class CombinedFoodDataset(Dataset):
    """
    Dataset que combina Food-101 con clases personalizadas.

    Las clases personalizadas se agregan después de las 101 de Food-101.
    Índices: 0-100 = Food-101, 101+ = clases mexicanas.
    """

    def __init__(self, root, split="train", transform=None,
                 download=True, custom_dir=None, train_ratio=0.8):
        """
        Args:
            root: Directorio raíz para Food-101
            split: "train" o "test"
            transform: Transformaciones de imagen
            download: Si descargar Food-101
            custom_dir: Directorio con clases personalizadas (subcarpetas)
            train_ratio: Proporción para train en clases personalizadas
        """
        self.transform = transform
        self.split = split

        # ─── Food-101 ───
        self.food101 = Food101(root=root, split=split,
                               transform=None, download=download)
        self.base_classes = list(self.food101.classes)

        # ─── Clases personalizadas ───
        self.custom_samples = []
        self.custom_classes = []

        if custom_dir and os.path.isdir(custom_dir):
            custom_folders = sorted([
                d for d in os.listdir(custom_dir)
                if os.path.isdir(os.path.join(custom_dir, d))
            ])

            for folder in custom_folders:
                folder_path = os.path.join(custom_dir, folder)
                images = [
                    os.path.join(folder_path, f)
                    for f in os.listdir(folder_path)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                ]

                if len(images) < 10:
                    print(f"  ⚠ {folder}: solo {len(images)} imágenes, saltando (mín 10)")
                    continue

                # Dividir en train/test de forma determinista
                random.seed(42)
                random.shuffle(images)
                split_idx = int(len(images) * train_ratio)

                if split == "train":
                    selected = images[:split_idx]
                else:
                    selected = images[split_idx:]

                class_idx = len(self.base_classes) + len(self.custom_classes)
                self.custom_classes.append(folder)

                for img_path in selected:
                    self.custom_samples.append((img_path, class_idx))

        # Lista completa de clases
        self.classes = self.base_classes + self.custom_classes
        self.num_classes = len(self.classes)

        print(f"  [{split}] Food-101: {len(self.food101)} | "
              f"Custom: {len(self.custom_samples)} ({len(self.custom_classes)} clases) | "
              f"Total clases: {self.num_classes}")

    def __len__(self):
        return len(self.food101) + len(self.custom_samples)

    def __getitem__(self, idx):
        if idx < len(self.food101):
            # Food-101
            img, label = self.food101[idx]
        else:
            # Clase personalizada
            custom_idx = idx - len(self.food101)
            img_path, label = self.custom_samples[custom_idx]
            img = Image.open(img_path).convert("RGB")

        if self.transform:
            img = self.transform(img)

        return img, label
