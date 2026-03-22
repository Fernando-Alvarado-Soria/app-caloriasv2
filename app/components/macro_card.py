from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle


class MacroCard(BoxLayout):
    """Widget reutilizable para mostrar un macronutriente."""
    title = StringProperty("Macro")
    value = NumericProperty(0)
    unit = StringProperty("g")
    bg_color = StringProperty("#E3F2FDFF")
    text_color = StringProperty("#1565C0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(8)
        self.size_hint_y = None
        self.height = dp(80)
        self.bind(pos=self._update_bg, size=self._update_bg,
                  bg_color=self._update_bg)
        self._bg_rect = None
        self._bg_color = None
        self._build()

    def _build(self):
        self._value_label = Label(
            font_size=sp(22),
            bold=True,
        )
        self._title_label = Label(
            font_size=sp(11),
            color=(0.4, 0.4, 0.4, 1),
        )
        self.add_widget(self._value_label)
        self.add_widget(self._title_label)
        self._update_text()
        self.bind(value=lambda *_: self._update_text(),
                  title=lambda *_: self._update_text(),
                  text_color=lambda *_: self._update_text())

    def _update_text(self):
        self._value_label.text = f"{round(self.value, 1)}{self.unit}"
        self._value_label.color = get_color_from_hex(self.text_color)
        self._title_label.text = self.title

    def _update_bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=get_color_from_hex(self.bg_color))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(12)])
