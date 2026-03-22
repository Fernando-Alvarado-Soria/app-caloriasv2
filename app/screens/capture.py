import os
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from plyer import filechooser


class CaptureScreen(Screen):
    image_path = StringProperty("")
    status_text = StringProperty("Toma o selecciona una foto de tu comida")

    def select_from_gallery(self):
        """Abre el selector de archivos para elegir una imagen."""
        try:
            selection = filechooser.open_file(
                title="Selecciona una foto de comida",
                filters=[("Imágenes", "*.png", "*.jpg", "*.jpeg", "*.bmp")],
            )
            if selection:
                self.image_path = selection[0]
                self.status_text = os.path.basename(self.image_path)
        except Exception:
            self.status_text = "No se pudo abrir la galería"

    def take_photo(self):
        """
        Captura desde cámara.
        En escritorio simula con filechooser.
        En móvil se usará plyer.camera.
        """
        try:
            from plyer import camera
            photo_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "capture.jpg"
            )
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            camera.take_picture(filename=photo_path,
                                on_complete=self._on_camera_complete)
        except (NotImplementedError, ImportError):
            # Fallback en escritorio: abrir filechooser
            self.select_from_gallery()

    def _on_camera_complete(self, filepath):
        if filepath and os.path.exists(filepath):
            self.image_path = filepath
            self.status_text = "Foto capturada"

    def analyze(self):
        if not self.image_path:
            self.status_text = "Primero selecciona o toma una foto"
            return
        # Guardamos la ruta en el manager para que ResultScreen la use
        self.manager.get_screen("result").image_path = self.image_path
        self.manager.current = "result"

    def go_back(self):
        self.image_path = ""
        self.status_text = "Toma o selecciona una foto de tu comida"
        self.manager.current = "home"
