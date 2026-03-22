from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex

from app.database.db import get_meals_today, get_meals_history


class HistoryScreen(Screen):
    meals = ListProperty([])

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):
        self.meals = get_meals_history(limit=50)
        self._build_list()

    def show_today(self):
        self.meals = get_meals_today()
        self._build_list()

    def show_all(self):
        self.meals = get_meals_history(limit=50)
        self._build_list()

    def _build_list(self):
        container = self.ids.get("meals_list")
        if not container:
            return
        container.clear_widgets()

        if not self.meals:
            lbl = Label(
                text="No hay comidas registradas",
                font_size=sp(14),
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(40),
            )
            container.add_widget(lbl)
            return

        for meal in self.meals:
            row = self._make_row(meal)
            container.add_widget(row)

    def _make_row(self, meal):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=(dp(10), dp(5)),
            spacing=dp(8),
        )

        # Nombre de la comida
        left = BoxLayout(orientation="vertical", size_hint_x=0.55)
        left.add_widget(Label(
            text=meal["food_class"].capitalize(),
            font_size=sp(15),
            bold=True,
            color=get_color_from_hex("#212121"),
            halign="left",
            text_size=(None, None),
        ))
        date_str = meal["created_at"][:16].replace("T", "  ")
        left.add_widget(Label(
            text=f"{meal['portion']} · {meal['grams']}g  —  {date_str}",
            font_size=sp(11),
            color=(0.5, 0.5, 0.5, 1),
            halign="left",
            text_size=(None, None),
        ))
        row.add_widget(left)

        # Calorías
        cal_label = Label(
            text=f"{int(meal['calories'])} kcal",
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex("#2E7D32"),
            size_hint_x=0.25,
        )
        row.add_widget(cal_label)

        # Macros compactos
        macros = Label(
            text=f"P{meal['protein']} C{meal['carbs']} G{meal['fat']}",
            font_size=sp(10),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.2,
        )
        row.add_widget(macros)

        return row

    def go_back(self):
        self.manager.current = "home"
