# game/trajectory_screen.py

from typing import List, Optional, Tuple
from math import hypot

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.clock import Clock

# Tus clases
from game.slingshot_player import SlingshotPlayer
from game.trajectory import Trajectory
from game.physics_projectile import PhysicsProjectile
from game.level1 import Level1Spec   # paredes + waypoints


class TrajectoryGameScreen(Widget):
    """
    Nivel 1: el jugador lanza proyectiles (huevos) con una resortera.
    El proyectil cae por gravedad y **choca contra las paredes** definidas
    en Level1Spec. Más adelante aquí mismo se pueden spawnear enemigos
    que usen los waypoints de ese nivel.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # -------------------------------------------------
        # 1) Fondo
        # -------------------------------------------------
        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo2.png",
                size=(Window.width, Window.height),
                pos=(0, 0),
            )

        # -------------------------------------------------
        # 2) Cargar nivel (paredes + waypoints)
        #    IMPORTANTE: lo hacemos ANTES de poner jugador,
        #    así el jugador queda encima de las paredes.
        # -------------------------------------------------
        self.level_spec: Level1Spec = Level1Spec()
        self.wall_widgets, self.wall_rects = self.level_spec.realize(self)
        # wall_rects = lista de (x, y, w, h) para colisiones

        # -------------------------------------------------
        # 3) Jugador tipo resortera
        # -------------------------------------------------
        self.player = SlingshotPlayer()
        # un poco más arriba del piso
        self.player.pos = (50, 100)
        self.add_widget(self.player)

        # -------------------------------------------------
        # 4) Trayectoria (los puntitos)
        # -------------------------------------------------
        self.trajectory = Trajectory()
        self.add_widget(self.trajectory)

        # -------------------------------------------------
        # 5) Estado de arrastre
        # -------------------------------------------------
        self.is_dragging: bool = False
        self.drag_start: Optional[Tuple[float, float]] = None
        self.current_force: Tuple[float, float] = (0.0, 0.0)

        # tope de distancia que se puede arrastrar (para no disparar a la luna)
        self.max_drag_distance: float = 180.0
        # factor conversión px de drag -> velocidad
        # (ajusta este número si quieres que salga más fuerte)
        self.launch_power: float = 7.5

        # -------------------------------------------------
        # 6) Lista de proyectiles activos
        # -------------------------------------------------
        self.projectiles: List[PhysicsProjectile] = []

        # -------------------------------------------------
        # 7) Bucle de juego
        # -------------------------------------------------
        Clock.schedule_interval(self.update, 1 / 60)

    # =====================================================
    # EVENTOS DE TOUCH
    # =====================================================
    def on_touch_down(self, touch):
        # Solo empezamos a arrastrar si tocamos al jugador
        if self.player.collide_point(*touch.pos):
            self.is_dragging = True
            self.drag_start = self.player.center  # punto fijo de disparo
            self.player.set_dragging(True)
            self.trajectory.show()
            return True

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.is_dragging:
            return super().on_touch_move(touch)

        # vector desde el punto fijo hacia donde estamos arrastrando
        sx, sy = self.drag_start
        tx, ty = touch.pos
        dx = tx - sx
        dy = ty - sy

        # en una resortera el disparo es en la dirección contraria al arrastre
        # o sea, si arrastro hacia abajo a la derecha, disparo hacia arriba a la izquierda
        # así que invertimos:
        vx = -dx
        vy = -dy

        # limitar la distancia de arrastre
        drag_dist = hypot(dx, dy)
        if drag_dist > self.max_drag_distance and drag_dist > 0:
            # normalizamos y escalamos al máximo
            scale = self.max_drag_distance / drag_dist
            vx *= scale
            vy *= scale

        # guardamos el vector de lanzamiento ya escalado
        self.current_force = (vx * self.launch_power, vy * self.launch_power)

        # actualizar los puntitos de trayectoria
        self.trajectory.update_dots(self.drag_start, self.current_force)

        return True

    def on_touch_up(self, touch):
        if not self.is_dragging:
            return super().on_touch_up(touch)

        # soltar -> disparar
        self.is_dragging = False
        self.player.set_dragging(False)
        self.trajectory.hide()

        # crear proyectil
        self.spawn_projectile(self.current_force)

        # reset
        self.current_force = (0.0, 0.0)
        self.drag_start = None

        return True

    # =====================================================
    # LÓGICA DE DISPARO
    # =====================================================
    def spawn_projectile(self, velocity: Tuple[float, float]):
        """
        Crea un PhysicsProjectile en la boca de la resortera
        y le pone la velocidad calculada.
        """
        proj = PhysicsProjectile(source="images/huevo.png")
        proj.size_hint = (None, None)
        proj.size = (38, 38)

        # lo ponemos más o menos en el centro del jugador
        proj.center = self.player.center

        # IMPORTANTÍSIMO: igualar la gravedad con la de tu widget de trayectoria
        # (tu Trajectory usa GRAVITY_FORCE = -150.0)
        proj.gravity = -150.0

        # velocidad calculada por el arrastre
        proj.velocity_x = float(velocity[0])
        proj.velocity_y = float(velocity[1])

        self.add_widget(proj)
        self.projectiles.append(proj)

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, dt: float):
        """
        Actualiza todos los proyectiles y aplica colisiones contra
        las paredes que vinieron de Level1Spec.
        """
        # hacemos copia para poder remover
        for proj in self.projectiles[:]:
            # aquí usamos TU método nuevo con paredes
            proj.update_with_walls(
                dt,
                self.wall_rects,
                on_impact=self.on_projectile_impact
            )

            if not proj.alive:
                # quitar de la escena
                if proj.parent is not None:
                    self.remove_widget(proj)
                self.projectiles.remove(proj)

    def on_projectile_impact(self, x: float, y: float):
        """
        Callback cuando un proyectil pega una pared.
        Aquí luego puedes:
        - hacer una explosión
        - dañar a un enemigo si está cerca
        - contar impacto en la pared
        """
        # por ahora solo un print
        # print(f"💥 impacto en ({x:.1f}, {y:.1f})")
        pass

    # =====================================================
    # POR SI CAMBIA EL TAMAÑO DE LA VENTANA
    # =====================================================
    def on_size(self, *args):
        # actualizar fondo
        if hasattr(self, "bg"):
            self.bg.size = (self.width, self.height)
            self.bg.pos = (0, 0)