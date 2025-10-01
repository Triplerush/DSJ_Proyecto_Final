from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App
import math

from .player import Player
from .enemy import Enemy


class GameScreen(Widget):
    score = NumericProperty(0)
    score_text = StringProperty("Score: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player()
        self.add_widget(self.player)

        self.enemies = []

        self.label = Label(text=self.score_text,
                           font_size='24sp',
                           color=(1, 1, 1, 1),
                           size_hint=(0.3, 0.1),
                           pos_hint={'x': 0.02, 'top': 0.98},
                           halign="left", valign="top")
        self.add_widget(self.label)

        Clock.schedule_interval(self.spawn_enemy, 2)
        Clock.schedule_interval(self.update, 1 / 60)
        Clock.schedule_interval(self.add_score, 1)

    def spawn_enemy(self, dt):
        enemy = Enemy(self.player)
        self.enemies.append(enemy)
        self.add_widget(enemy)

    def update(self, dt):
        for enemy in self.enemies[:]:
            enemy.update(dt)

            if not enemy.is_homing and enemy.y < -50:
                self.remove_widget(enemy)
                self.enemies.remove(enemy)

            if self.check_collision(self.player, enemy):
                print("❌ ¡Perdiste!")
                App.get_running_app().stop()

        self.label.text = self.score_text

    def add_score(self, dt):
        self.score += 1
        self.score_text = f"Score: {self.score}"

    def check_collision(self, player, enemy):
        px, py = player.center_x, player.center_y
        ex, ey = enemy.center_x, enemy.center_y

        pr = player.sprite.width / 2 * 0.8
        er = enemy.sprite.width / 2 * 0.8

        distancia = math.sqrt((px - ex)**2 + (py - ey)**2)
        return distancia < (pr + er)

    def on_touch_down(self, touch):
        self.player.move_to(touch)

    def on_touch_move(self, touch):
        self.player.move_to(touch)
