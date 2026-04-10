"""
Tabla nutricional base — valores promedio por 100 g.
Fuente de referencia: USDA FoodData Central (valores simplificados).

Cada entrada:  (calorías, proteína_g, carbohidratos_g, grasa_g)
"""

FOOD_TABLE: dict[str, tuple[float, float, float, float]] = {
    # Comida rápida
    "pizza":             (266, 11.4, 33.0, 10.4),
    "hamburguesa":       (254, 17.0, 24.0, 10.0),
    "hot dog":           (290, 10.0, 24.0, 18.0),
    "papas fritas":      (312, 3.4,  41.0, 15.0),
    "nuggets":           (297, 15.0, 18.0, 18.0),

    # Mexicana
    "tacos":             (226, 12.0, 20.0, 11.0),
    "burrito":           (206, 8.7,  25.0, 8.0),
    "enchiladas":        (168, 8.0,  16.0, 8.5),
    "quesadilla":        (260, 11.0, 24.0, 13.0),
    "tamales":           (210, 7.5,  24.0, 10.0),
    "chilaquiles":       (180, 7.0,  17.0, 9.0),
    "pozole":            (100, 6.0,  12.0, 3.0),
    "tostadas":          (230, 9.0,  22.0, 12.0),
    "caldo de pollo":    (75,  6.0,  5.0,  3.0),
    "tacos dorados":     (245, 10.0, 22.0, 13.0),
    "sopes":             (210, 7.0,  22.0, 10.0),
    "gorditas":          (230, 8.0,  26.0, 10.0),
    "tlacoyos":          (195, 6.0,  25.0, 8.0),
    "elote":             (96,  3.4,  19.0, 1.5),
    "torta mexicana":    (280, 14.0, 30.0, 12.0),
    "molletes":          (220, 9.0,  28.0, 8.0),
    "huevos rancheros":  (180, 12.0, 10.0, 11.0),
    "arroz rojo":        (140, 3.0,  28.0, 2.0),
    "frijoles":          (127, 8.7,  21.0, 0.5),
    "carne en su jugo":  (145, 14.0, 6.0,  7.0),
    "birria":            (220, 18.0, 5.0,  14.0),
    "menudo":            (110, 12.0, 6.0,  4.5),
    "flautas":           (255, 10.0, 24.0, 14.0),
    "mole":              (180, 10.0, 15.0, 9.0),
    "chiles rellenos":   (165, 8.0,  12.0, 10.0),

    # Platos principales
    "pollo asado":       (190, 29.0,  0.0,  7.5),
    "carne asada":       (250, 26.0,  0.0, 15.0),
    "pescado frito":     (232, 16.0, 11.0, 14.0),
    "pescado a la plancha": (120, 22.0, 0.0,  3.0),
    "arroz blanco":      (130, 2.7,  28.0,  0.3),
    "arroz con pollo":   (170, 12.0, 20.0,  5.0),
    "spaghetti":         (158, 5.8,  31.0,  0.9),
    "lasagna":           (135, 8.0,  13.0,  5.5),
    "sushi":             (143, 5.8,  26.0,  1.5),
    "ramen":             (190, 8.0,  26.0,  6.0),

    # Ensaladas y ligero
    "ensalada":          (20,  1.5,   3.5,  0.2),
    "ensalada cesar":    (127, 6.0,   7.0,  8.5),
    "sopa de verduras":  (40,  1.5,   7.0,  0.5),

    # Desayuno
    "huevos revueltos":  (149, 10.0,  1.6, 11.0),
    "huevos fritos":     (196, 14.0,  0.8, 15.0),
    "pancakes":          (227,  6.0, 28.0, 10.0),
    "cereal":            (379,  7.0, 84.0,  1.5),
    "pan tostado":       (313,  9.0, 50.0,  8.0),
    "fruta":             (52,   0.3, 14.0,  0.2),

    # Postres
    "pastel":            (257,  3.0, 35.0, 12.0),
    "helado":            (207,  3.5, 24.0, 11.0),
    "galletas":          (480,  5.0, 65.0, 22.0),
    "dona":              (421,  5.0, 49.0, 23.0),
    "churros":           (389,  4.0, 40.0, 24.0),

    # Bebidas / snacks
    "sandwich":          (250, 12.0, 28.0, 10.0),
    "croissant":         (406,  8.0, 46.0, 21.0),
}

# Multiplicadores de porción respecto a 100 g
PORTION_MULTIPLIERS: dict[str, float] = {
    "pequeña": 0.75,
    "mediana": 1.0,
    "grande":  1.5,
}


def estimate_nutrition(food_class: str, portion: str = "mediana",
                       grams: float | None = None):
    """
    Devuelve un dict con la estimación nutricional.
    Si se pasan gramos, se usan directamente.
    Si no, se usa el multiplicador de porción sobre un estimado base de 150 g.
    """
    key = food_class.lower().strip()
    if key not in FOOD_TABLE:
        return None

    cal_100, prot_100, carb_100, fat_100 = FOOD_TABLE[key]

    if grams is not None and grams > 0:
        factor = grams / 100.0
    else:
        base_grams = 150.0  # porción base estimada
        multiplier = PORTION_MULTIPLIERS.get(portion, 1.0)
        grams = base_grams * multiplier
        factor = grams / 100.0

    return {
        "food_class": key,
        "portion": portion,
        "grams": round(grams, 1),
        "calories": round(cal_100 * factor, 1),
        "protein": round(prot_100 * factor, 1),
        "carbs": round(carb_100 * factor, 1),
        "fat": round(fat_100 * factor, 1),
    }


def get_food_classes():
    """Devuelve la lista de clases disponibles ordenada."""
    return sorted(FOOD_TABLE.keys())
