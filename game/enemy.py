from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
import random, math


class Enemy(Widget):
    def __init__(self, player, is_homing=False, **kwargs):
        super().__init__(**kwargs)
        self.sprite = Image(source="assets/images/enemy.png", size_hint=(None, None))
        self.sprite.size = (60, 60)
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
