from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock


class Player(Widget):
    # Posición objetivo del jugador (hacia dónde moverse)
    target_x = NumericProperty(0)
    target_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Imagen del jugador (asegúrate que exista el archivo en assets/images)
        self.sprite = Image(source="assets/images/player.png", size_hint=(None, None))
        self.sprite.size = (80, 80)
        self.add_widget(self.sprite)

        # Posición inicial
        self.center_x = Window.width / 2
        self.y = 50
        self.target_x = self.center_x
        self.target_y = self.center_y
        self.update_sprite()

        # Actualización continua (60 FPS aprox)
        Clock.schedule_interval(self.update, 1/60)

    def update_sprite(self):
        """Mantiene el sprite alineado con el widget"""
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        """Se ejecuta en cada frame y mueve suavemente al jugador hacia el objetivo"""
        speed = 15  # cuanto mayor, más rápido se mueve

        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y

        # Movimiento en X
        if abs(dx) > speed:
            self.center_x += speed if dx > 0 else -speed
        else:
            self.center_x = self.target_x

        # Movimiento en Y
        if abs(dy) > speed:
            self.center_y += speed if dy > 0 else -speed
        else:
            self.center_y = self.target_y

        self.update_sprite()

    def move_to(self, touch):
        """Actualiza la posición objetivo"""
        self.target_x = touch.x
        self.target_y = touch.y


class GameScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player()
        self.add_widget(self.player)

    def on_touch_down(self, touch):
        self.player.move_to(touch)

    def on_touch_move(self, touch):
        self.player.move_to(touch)


class MyGameApp(App):
    def build(self):
        return GameScreen()


if __name__ == "__main__":
    MyGameApp().run()
