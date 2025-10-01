from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock  
import random, math


class Enemy(Widget):
    def __init__(self, player, is_homing=False, **kwargs):
        super().__init__(**kwargs)

        # --- Animación del enemigo ---
        self.animation_frames = [
            "images/enemigo1.png",
            "images/enemigo2.png",
            "images/enemigo3.png",
            "images/enemigo4.png"
        ]
        self.current_frame = 0
        self.animation_speed = 0.1  # 10 FPS

        # Inicializar sprite con el primer frame
        self.sprite = Image(source=self.animation_frames[self.current_frame], size_hint=(None, None))
        # -------------------------------------------

        self.sprite.size = (120, 120)
        self.add_widget(self.sprite)

        # Posición inicial
        self.center_x = random.randint(50, Window.width - 50)
        self.y = Window.height + 50
        self.update_sprite()

        # Propiedades
        self.speed = 4
        self.is_homing = is_homing
        self.player = player

        # Vida en segundos solo para homing
        self.lifetime = 5 if self.is_homing else None

        # --- MODIFICACIÓN: Iniciar animación ---
        Clock.schedule_interval(self.animate_enemy, self.animation_speed)
        # ---------------------------------------

    def animate_enemy(self, dt):
        """Cambia el sprite del enemigo para crear una animación."""
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        self.sprite.source = self.animation_frames[self.current_frame]

    def update_sprite(self):
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        if self.is_homing:
            # Seguir al jugador
            dx = self.player.center_x - self.center_x
            dy = self.player.center_y - self.center_y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.center_x += (dx / dist) * self.speed
                self.center_y += (dy / dist) * self.speed

            # Reducir vida
            self.lifetime -= dt
            if self.lifetime <= 0:
                return False  # marcar para eliminar
        else:
            # Movimiento normal hacia abajo
            self.y -= self.speed * 1.5
            if self.y < -50:
                return False  # eliminar si sale de pantalla

        self.update_sprite()
        return True
