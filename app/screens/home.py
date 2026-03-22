from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty
from app.database.db import get_meals_today


class HomeScreen(Screen):
    total_calories = NumericProperty(0)
    total_protein = NumericProperty(0)
    total_carbs = NumericProperty(0)
    total_fat = NumericProperty(0)
    meals_count = NumericProperty(0)

    def on_pre_enter(self):
        self.refresh_summary()

    def refresh_summary(self):
        meals = get_meals_today()
        self.meals_count = len(meals)
        self.total_calories = round(sum(m["calories"] for m in meals), 1)
        self.total_protein = round(sum(m["protein"] for m in meals), 1)
        self.total_carbs = round(sum(m["carbs"] for m in meals), 1)
        self.total_fat = round(sum(m["fat"] for m in meals), 1)

    def go_capture(self):
        self.manager.current = "capture"

    def go_history(self):
        self.manager.current = "history"
