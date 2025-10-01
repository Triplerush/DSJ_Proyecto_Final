from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock
import random
import math


class Player(Widget):
    target_x = NumericProperty(0)
    target_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite = Image(source="assets/images/player.png", size_hint=(None, None))
        self.sprite.size = (80, 80)
        self.add_widget(self.sprite)

        self.center_x = Window.width / 2
        self.y = 50
        self.target_x = self.center_x
        self.target_y = self.center_y
        self.update_sprite()

        Clock.schedule_interval(self.update, 1/60)

    def update_sprite(self):
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        speed = 50
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


class Enemy(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite = Image(source="assets/images/enemy.png", size_hint=(None, None))
        self.sprite.size = (60, 60)
        self.add_widget(self.sprite)

        # posición inicial aleatoria arriba de la pantalla
        self.center_x = random.randint(50, Window.width - 50)
        self.y = Window.height + 50
        self.update_sprite()

    def update_sprite(self):
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        """Hace que el enemigo baje hacia abajo"""
        self.y -= 5
        self.update_sprite()


class GameScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player()
        self.add_widget(self.player)

        self.enemies = []
        # Generar enemigos cada 2 segundos
        Clock.schedule_interval(self.spawn_enemy, 2)
        # Actualizar colisiones y movimiento de enemigos
        Clock.schedule_interval(self.update, 1/60)

    def spawn_enemy(self, dt):
        enemy = Enemy()
        self.enemies.append(enemy)
        self.add_widget(enemy)

    def update(self, dt):
        # Actualizar enemigos
        for enemy in self.enemies[:]:
            enemy.update(dt)
            # Eliminar si sale de la pantalla
            if enemy.y < -50:
                self.remove_widget(enemy)
                self.enemies.remove(enemy)

            # Detectar colisión con jugador
            if self.check_collision(self.player, enemy):
                print("¡Perdiste!")
                App.get_running_app().stop()

    def check_collision(self, player, enemy):
        """Colisión circular más precisa"""
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


class MyGameApp(App):
    def build(self):
        return GameScreen()


if __name__ == "__main__":
    MyGameApp().run()
