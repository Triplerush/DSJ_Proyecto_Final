from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.lang import Builder

# Cargamos el archivo .kv
Builder.load_file("mi_juego.kv")

class Cuadrado(Widget):
    # Posición del cuadrado
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)

    def on_touch_move(self, touch):
        # Mover el cuadrado a la posición del toque/mouse
        self.pos_x = touch.x - self.width / 2
        self.pos_y = touch.y - self.height / 2

class MiJuego(Widget):
    pass

class MiJuegoApp(App):
    def build(self):
        return MiJuego()

if __name__ == "__main__":
    MiJuegoApp().run()
