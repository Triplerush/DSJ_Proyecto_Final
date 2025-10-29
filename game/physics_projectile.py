# game/physics_projectile.py
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window

# Esta es nuestra "gravedad" en píxeles/segundo^2.
# 9.81 es muy poco para píxeles, así que usamos un valor mayor.
# ¡Debe ser el mismo que en trajectory.py!
GRAVITY_FORCE = -150.0 

class PhysicsProjectile(Widget):
    def __init__(self, start_pos, **kwargs):
        super().__init__(**kwargs)
        
        self.sprite = Image(source="images/huevo.png",
                            size_hint=(None, None),
                            size=(45, 45))
        self.add_widget(self.sprite)
        
        # Posición inicial
        self.center = start_pos
        self.sprite.center = self.center
        
        # Físicas (como el Rigidbody de Unity)
        self.velocity = [0, 0] # (vx, vy)
        self.is_kinematic = True # No se moverá hasta ser lanzado
        
    def push(self, force_vector):
        """
        Aplica la fuerza de lanzamiento. 
        En Kivy, trataremos esta 'fuerza' como la velocidad inicial.
        """
        self.velocity = [force_vector[0], force_vector[1]]
        self.is_kinematic = False # ¡Activar físicas!
        
    def update(self, dt):
        """Actualiza la física del proyectil cada frame."""
        if self.is_kinematic:
            return True # Sigue vivo, pero quieto
            
        # --- Simulación de Física (como en Unity) ---
        
        # 1. Aplicar gravedad a la velocidad
        # v = v0 + g * t
        self.velocity[1] += GRAVITY_FORCE * dt
        
        # 2. Aplicar velocidad a la posición
        # p = p0 + v * t
        self.center_x += self.velocity[0] * dt
        self.center_y += self.velocity[1] * dt
        
        # 3. Actualizar el sprite
        self.sprite.center = self.center
        
        # 4. Verificar si salió de pantalla (para eliminarlo)
        if self.top < 0 or self.right < 0 or self.x > Window.width:
            return False # Marcar para eliminar
            
        return True # Sigue vivo