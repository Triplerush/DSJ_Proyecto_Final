from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
import math


class Projectile(Widget):
    def __init__(self, start_x, start_y, target_x, target_y, **kwargs):
        super().__init__(**kwargs)
        
        # Sprite del proyectil (IMPORTANTE: crear nuevo Image independiente)
        self.sprite = Image(
            source="images/huevo.png", 
            size_hint=(None, None),
            size=(40, 40)
        )
        self.add_widget(self.sprite)
        
        # Posición inicial del proyectil
        self.center_x = start_x
        self.center_y = start_y
        
        # Calcular dirección hacia el objetivo
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            self.velocity_x = (dx / dist) * 8  # Velocidad del proyectil
            self.velocity_y = (dy / dist) * 8
        else:
            self.velocity_x = 0
            self.velocity_y = -8
        
        self.update_sprite()
    
    def update_sprite(self):
        """Actualiza la posición visual del sprite del proyectil"""
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y
    
    def update(self, dt):
        """Actualiza la posición del proyectil cada frame"""
        # Mover el proyectil
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y
        
        # Verificar si salió de la pantalla
        if (self.center_x < -50 or self.center_x > Window.width + 50 or
            self.center_y < -50 or self.center_y > Window.height + 50):
            return False  # Marcar para eliminar
        
        self.update_sprite()
        return True