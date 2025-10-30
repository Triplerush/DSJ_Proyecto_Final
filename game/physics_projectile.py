# game/physics_projectile.py
from typing import List, Optional, Callable
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty

from .geometry import Rect
from .collision import move_with_collisions


class PhysicsProjectile(Image):
    """
    Proyectil balístico con gravedad y colisiones vs paredes (AABB).
    - Llama update_with_walls(dt, walls, on_impact)
    - Si 'bounce_enabled' es False (por defecto), se destruye al impactar.
      Si es True, rebota con restitución 'restitution'.
    """

    # Velocidad en px/s
    velocity_x = NumericProperty(0.0)
    velocity_y = NumericProperty(0.0)

    # Gravedad en px/s^2 (negativa hacia abajo)
    gravity = NumericProperty(-980.0)

    # Vida del proyectil (si False, debe eliminarse de la escena)
    alive = BooleanProperty(True)

    # Rebote opcional
    bounce_enabled = BooleanProperty(False)
    restitution = NumericProperty(0.5)  # 0..1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Asegurar un tamaño por defecto si no lo pasan
        if not self.width or not self.height:
            self.size_hint = (None, None)
            self.size = (32, 32)
        # Si no pasaron source y quieres un sprite por defecto, descomenta:
        # if not getattr(self, "source", None):
        #     self.source = "images/huevo.png"

        # Por si acaso, inicializamos flags coherentes
        if not hasattr(self, "alive"):
            self.alive = True

    def update_with_walls(
        self,
        dt: float,
        walls: List[Rect],
        on_impact: Optional[Callable[[float, float], None]] = None,
    ):
        """
        Integra gravedad y aplica movimiento con colisiones contra paredes.
        Si hay impacto:
          - bounce_enabled=False: se destruye y dispara callback on_impact.
          - bounce_enabled=True: rebota con pérdida (restitution).
        """

        if not self.alive:
            return

        # 1) Integración de gravedad
        self.velocity_y += self.gravity * dt

        # 2) Movimiento con colisiones (AABB del sprite actual)
        w = max(1.0, float(self.width))
        h = max(1.0, float(self.height))

        nx, ny, nvx, nvy, collided = move_with_collisions(
            self.x,
            self.y,
            w,
            h,
            float(self.velocity_x),
            float(self.velocity_y),
            dt,
            walls,
        )

        # 3) Aplicar posiciones
        self.x, self.y = nx, ny

        if collided:
            if self.bounce_enabled:
                # Si el resolver anuló una componente, invertimos la original con restitución
                if nvx == 0.0 and abs(self.velocity_x) > 1e-3:
                    self.velocity_x = -self.velocity_x * float(self.restitution)
                else:
                    self.velocity_x = nvx

                if nvy == 0.0 and abs(self.velocity_y) > 1e-3:
                    self.velocity_y = -self.velocity_y * float(self.restitution)
                else:
                    self.velocity_y = nvy

                # Si la energía es muy baja, damos por terminado
                if (self.velocity_x ** 2 + self.velocity_y ** 2) < 25.0:
                    self.alive = False
                    if on_impact:
                        on_impact(self.center_x, self.center_y)
            else:
                # Sin rebote: destruir al impactar
                self.alive = False
                if on_impact:
                    on_impact(self.center_x, self.center_y)
        else:
            # Sin colisión: simplemente actualizamos velocidades resueltas
            self.velocity_x = nvx
            self.velocity_y = nvy

    # (Opcional) método 'update' para compatibilidad si en otro lado lo llaman
    def update(self, dt: float):
        """Compat: si alguien llama update(dt) en vez de update_with_walls."""
        self.velocity_y += self.gravity * dt
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
