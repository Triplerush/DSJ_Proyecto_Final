from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock  
import random, math
from game.utils import limit_vector, normalize_vector

class Enemy(Widget):
    def __init__(self, player, is_homing=False, use_flocking=False, **kwargs):
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

        #  Propiedades para flocking
        self.use_flocking = use_flocking
        self.velocity_x = 0
        self.velocity_y = -self.speed  # Inicialmente hacia abajo
        self.acceleration_x = 0
        self.acceleration_y = 0
        self.max_speed = 6
        self.max_force = 0.3


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

    def apply_force(self, force_x, force_y):
        """Aplica una fuerza a la aceleración (usado para flocking)"""
        self.acceleration_x += force_x
        self.acceleration_y += force_y
    
    def update(self, dt, flocking_force=None):
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
        
        if self.use_flocking and flocking_force:
            # Aplicar fuerza de flocking
            force_x, force_y = flocking_force
            # LOG: Debug ocasional
            if not hasattr(self, 'log_counter'):
                self.log_counter = 0
            self.log_counter += 1
            if self.log_counter % 120 == 0:
                print(f"   🐦 Flocking enemy at ({self.center_x:.0f}, {self.center_y:.0f}) | Force: ({force_x:.2f}, {force_y:.2f}) | Vel: ({self.velocity_x:.2f}, {self.velocity_y:.2f})")

            # Limitar la fuerza máxima
            force_x, force_y = limit_vector(force_x, force_y, self.max_force)
            self.apply_force(force_x, force_y)
            
            # Actualizar velocidad con aceleración
            self.velocity_x += self.acceleration_x
            self.velocity_y += self.acceleration_y
            
            # Limitar velocidad máxima
            self.velocity_x, self.velocity_y = limit_vector(
                self.velocity_x, self.velocity_y, self.max_speed
            )
            
            # Actualizar posición
            self.center_x += self.velocity_x
            self.center_y += self.velocity_y
            
            # Resetear aceleración para el próximo frame
            self.acceleration_x = 0
            self.acceleration_y = 0
            
            # Verificar si sale de pantalla
            if self.y < -200 or self.center_x < -100 or self.center_x > Window.width + 100:
                print(f"   ❌ Flocking enemy removed (out of bounds)")
                return False
        
        # 2. Si es HOMING (persigue al jugador)
        elif self.is_homing:
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

