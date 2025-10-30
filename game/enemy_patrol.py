from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.animation import Animation
import math, random


class PatrolEnemy(Widget):
    """Enemigo que patrulla entre varios waypoints con animación y colisión.
       Tiene flags is_dead y removed para una eliminación segura desde el GameScreen.
    """
    def __init__(self, waypoints, speed=3, **kwargs):
        super().__init__(**kwargs)

        # Animación del enemigo (usa las mismas imágenes que ya tienes)
        self.animation_frames = [
            "images/enemigo1.png",
            "images/enemigo2.png",
            "images/enemigo3.png",
            "images/enemigo4.png"
        ]
        self.current_frame = 0

        # Sprite (Image) del enemigo
        self.sprite = Image(
            source=self.animation_frames[self.current_frame],
            size_hint=(None, None),
            size=(100, 100),  # tamaño visible, más pequeño que antes
            opacity=1.0
        )
        self.add_widget(self.sprite)

        # Waypoints y movimiento
        self.waypoints = waypoints[:]  # lista de Waypoint (con .pos)
        self.current_wp = 0
        self.speed = speed

        # Flags para eliminación segura
        self.is_dead = False     # cuando se le golpea por primera vez
        self.removed = False     # cuando ya fue removido del padre / lista

        # Posición inicial: primer waypoint
        if self.waypoints:
            self.center_x, self.center_y = self.waypoints[0].pos
        else:
            self.center_x, self.center_y = (50, 50)

        self.update_sprite()

        # Programar animación y movimiento
        Clock.schedule_interval(self.animate_enemy, 0.12)
        Clock.schedule_interval(self._internal_update, 1 / 60)

        # Aleatorizar fase de animación (visual)
        self._anim_phase_offset = random.uniform(0, 0.12)

    def animate_enemy(self, dt):
        """Cambia frame para simular animación. Pausado si está muerto."""
        if self.is_dead:
            return
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        self.sprite.source = self.animation_frames[self.current_frame]

    def _internal_update(self, dt):
        """Wrapper para separar la lógica de movimiento y permitir que el owner lo elimine."""
        if self.is_dead:
            # si ya está muerto no se mueve; el GameScreen se encargará de removerlo
            return
        self.update(dt)

    def update(self, dt):
        """Mover al enemigo hacia el waypoint actual."""
        if self.is_dead or not self.waypoints:
            return

        target_x, target_y = self.waypoints[self.current_wp].pos
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        dist = math.hypot(dx, dy)

        if dist < 4:  # alcanza waypoint -> siguiente
            self.current_wp = (self.current_wp + 1) % len(self.waypoints)
        else:
            # movimiento proporcional a dt para consistencia con fps variable
            step = self.speed
            self.center_x += (dx / dist) * step
            self.center_y += (dy / dist) * step

            # rotación visual: usamos sprite.angle si disponible (Kivy Image soporta rotation via canvas)
            try:
                angle = math.degrees(math.atan2(dy, dx))
                # algunos proyectos usan texture rotation; aquí solo guardamos el cálculo
                # Si quieres aplicar rotación real, habría que redibujar el sprite con canvas rotation.
                self.sprite.angle = -angle + 90
            except Exception:
                pass

        self.update_sprite()

    def update_sprite(self):
        """Mantener sprite centrado."""
        # Aseguramos que el sprite exista
        if hasattr(self, "sprite") and self.sprite is not None:
            self.sprite.center_x = self.center_x
            self.sprite.center_y = self.center_y

    def destroy(self):
        """Inicia animación de muerte y marca is_dead.
           No elimina la instancia de la lista 'self.parent.enemies' (lo hace el GameScreen en su update).
        """
        if self.is_dead:
            return
        self.is_dead = True

        # Animación visual: disminuir y desvanecer
        anim = Animation(opacity=0.0, size=(24, 24), duration=0.28, t='out_quad')
        # Al completar la animación, dejamos que el GameScreen detecte is_dead y remueva el widget.
        anim.start(self.sprite)
