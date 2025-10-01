from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
import random, math


class Enemy(Widget):
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.sprite = Image(source="assets/images/enemy.png", size_hint=(None, None))
        self.sprite.size = (60, 60)
        self.add_widget(self.sprite)

        self.center_x = random.randint(50, Window.width - 50)
        self.y = Window.height + 50
        self.update_sprite()

        self.speed = 4
        self.is_homing = random.random() < 0.3  # 30% de probabilidad de seguir al jugador
        self.player = player

    def update_sprite(self):
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        if self.is_homing:
            dx = self.player.center_x - self.center_x
            dy = self.player.center_y - self.center_y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.center_x += (dx / dist) * self.speed
                self.center_y += (dy / dist) * self.speed
        else:
            self.y -= self.speed * 1.5

        self.update_sprite()