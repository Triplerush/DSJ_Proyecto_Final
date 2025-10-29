# game/slingshot_player.py
from kivy.uix.widget import Widget
from kivy.uix.image import Image

class SlingshotPlayer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Guardamos las texturas
        self.idle_sprite = "images/vicu1.png"
        self.drag_sprite = "images/vicu2.png"
        
        # Creamos la imagen inicial
        self.sprite = Image(source=self.idle_sprite,
                            size_hint=(None, None),
                            size=(160, 160))
        self.add_widget(self.sprite)

        # Hacemos que el tamaño del widget se ajuste al sprite
        self.size = self.sprite.size
        
    def on_pos(self, *args):
        """Actualiza la posición del sprite cuando el widget se mueve."""
        self.sprite.pos = self.pos
        
    def set_dragging(self, is_dragging):
        """Cambia el sprite del jugador basado en el estado de arrastre."""
        if is_dragging:
            self.sprite.source = self.drag_sprite
        else:
            self.sprite.source = self.idle_sprite