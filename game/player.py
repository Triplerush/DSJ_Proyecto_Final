from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock


class Player(Widget):
    target_x = NumericProperty(0)
    target_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # --- Animación del jugador ---
        # Lista de imágenes para la animación. Asegúrate que estén en esta ruta.
        self.animation_frames = [
            "images/ave1.png",
            "images/ave2.png",
            "images/ave3.png",
            "images/ave4.png"
        ]
        self.current_frame = 0
        self.animation_speed = 0.1  # Cambia de imagen cada 0.1 segundos (10 FPS)

        # Inicializar el sprite con la primera imagen de la animación
        self.sprite = Image(source=self.animation_frames[self.current_frame], size_hint=(None, None))
        # ----------------------------------------------

        self.sprite.size = (160, 160)
        self.add_widget(self.sprite)

        self.center_x = Window.width / 2
        self.y = 50
        self.target_x = self.center_x
        self.target_y = self.center_y
        self.update_sprite()

        Clock.schedule_interval(self.update, 1 / 60)

        # --- Iniciar el ciclo de animación ---
        Clock.schedule_interval(self.animate_player, self.animation_speed)
        # ----------------------------------------------------

    def animate_player(self, dt):
        """Cambia el sprite del jugador para crear una animación de aleteo."""
        # Avanza al siguiente frame y vuelve al inicio si llega al final (loop)
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        self.sprite.source = self.animation_frames[self.current_frame]

    def update_sprite(self):
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        speed = 15
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y

        if abs(dx) > speed:
            self.center_x += speed if dx > 0 else -speed
        else:
            self.center_x = self.target_x

        if abs(dy) > speed:
            self.center_y += speed if dy > 0 else -speed
        else:
            self.center_y = self.target_y

        self.update_sprite()

    def move_to(self, touch):
        self.target_x = touch.x
        self.target_y = touch.y
