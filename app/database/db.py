import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "calorias.db")


def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            food_class  TEXT NOT NULL,
            portion     TEXT NOT NULL DEFAULT 'mediana',
            grams       REAL NOT NULL DEFAULT 100,
            calories    REAL NOT NULL,
            protein     REAL NOT NULL DEFAULT 0,
            carbs       REAL NOT NULL DEFAULT 0,
            fat         REAL NOT NULL DEFAULT 0,
            image_path  TEXT,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_meal(food_class, portion, grams, calories, protein, carbs, fat,
              image_path=None):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meals (food_class, portion, grams, calories, protein,
                           carbs, fat, image_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (food_class, portion, grams, calories, protein, carbs, fat,
          image_path, datetime.now().isoformat()))
    conn.commit()
    meal_id = cursor.lastrowid
    conn.close()
    return meal_id


def get_meals_today():
    conn = _get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT * FROM meals WHERE created_at LIKE ? ORDER BY created_at DESC",
        (f"{today}%",)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_meals_history(limit=50):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM meals ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def delete_meal(meal_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    conn.commit()
    conn.close()
