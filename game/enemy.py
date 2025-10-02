from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock  
import random, math


class Enemy(Widget):
    def __init__(self, player, is_homing=False, **kwargs):
        super().__init__(**kwargs)

        # Referencias a imágenes de animación
        self.animation_frames = [
            "images/enemigo1.png",
            "images/enemigo2.png",
            "images/enemigo3.png",
            "images/enemigo4.png"
        ]
        self.current_frame = 0
        self.animation_speed = 0.1  # 10 FPS

        # IMPORTANTE: Crear UN NUEVO sprite Image para este enemigo
        self.sprite = Image(
            source=self.animation_frames[self.current_frame], 
            size_hint=(None, None),
            size=(120, 120)
        )
        self.add_widget(self.sprite)

        # Posición inicial
        self.center_x = random.randint(50, Window.width - 50)
        self.y = Window.height + 50
        self.update_sprite()

        # Propiedades de movimiento
        self.speed = 4
        self.is_homing = is_homing
        self.player = player

        # Vida en segundos solo para homing
        self.lifetime = 5 if self.is_homing else None

        # Sistema de disparo
        self.shoot_cooldown = 5.0  # Dispara cada 5 segundos
        self.time_since_last_shot = random.uniform(0, 3)  # Randomizar inicio

        # Iniciar animación del enemigo
        Clock.schedule_interval(self.animate_enemy, self.animation_speed)

    def animate_enemy(self, dt):
        """Cambia el sprite del enemigo para crear una animación."""
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        # Cambiar la fuente de la imagen
        self.sprite.source = self.animation_frames[self.current_frame]

    def update_sprite(self):
        """Actualiza la posición del sprite del enemigo"""
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        """Actualiza el estado del enemigo cada frame"""
        # Actualizar temporizador de disparo
        self.time_since_last_shot += dt
        
        # Disparar si es tiempo y el enemigo está visible en pantalla
        if (self.time_since_last_shot >= self.shoot_cooldown and 
            0 < self.center_y < Window.height):
            
            # Llamar al método de disparo si existe
            if hasattr(self, 'shoot_projectile') and callable(self.shoot_projectile):
                self.shoot_projectile()
            self.time_since_last_shot = 0
        
        # Lógica de movimiento
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
    