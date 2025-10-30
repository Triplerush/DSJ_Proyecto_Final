# game/trajectory_screen.py

from typing import List, Optional, Tuple
from math import hypot, sqrt

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.clock import Clock

# Tus clases
from game.slingshot_player import SlingshotPlayer
from game.trajectory import Trajectory
from game.physics_projectile import PhysicsProjectile
from game.level1 import Level1Spec
from game.enemy_patrol import PatrolEnemy


class TrajectoryGameScreen(Widget):
    """
    Nivel 1: el jugador lanza proyectiles (huevos) con una resortera.
    El proyectil cae por gravedad, choca contra paredes y puede
    destruir enemigos que patrullan usando los waypoints del nivel.
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
        # -------------------------------------------------
        self.level_spec: Level1Spec = Level1Spec()
        self.wall_widgets, self.wall_rects, self.waypoints = self.level_spec.realize(self)

        # -------------------------------------------------
        # 3) Jugador tipo resortera
        # -------------------------------------------------
        self.player = SlingshotPlayer()
        self.player.pos = (50, 100)
        self.add_widget(self.player)

        # -------------------------------------------------
        # 4) Trayectoria (los puntitos)
        # -------------------------------------------------
        self.trajectory = Trajectory()
        self.add_widget(self.trajectory)

        # -------------------------------------------------
        # 5) Estado de arrastre y lanzamiento
        # -------------------------------------------------
        self.is_dragging: bool = False
        self.drag_start: Optional[Tuple[float, float]] = None
        self.current_force: Tuple[float, float] = (0.0, 0.0)
        self.max_drag_distance: float = 180.0
        self.launch_power: float = 7.5

        # -------------------------------------------------
        # 6) Listas activas
        # -------------------------------------------------
        self.projectiles: List[PhysicsProjectile] = []
        self.enemies: List[PatrolEnemy] = []

        # -------------------------------------------------
        # 7) Crear enemigos que patrullan los waypoints
        # -------------------------------------------------
        self.spawn_patrol_enemies()

        # -------------------------------------------------
        # 8) Bucle de juego
        # -------------------------------------------------
        Clock.schedule_interval(self.update, 1 / 60)

    # =====================================================
    # CREACIÓN DE ENEMIGOS MEJORADA
    # =====================================================
    def spawn_patrol_enemies(self):
        """
        Crea enemigos con patrones de patrullaje variados y estratégicos.
        Incluye:
        - Patrullas lineales (ida y vuelta)
        - Patrullas circulares (recorrido completo)
        - Patrullas triangulares
        - Diferentes velocidades para variar dificultad
        """
        if not self.waypoints or len(self.waypoints) < 2:
            return

        num_waypoints = len(self.waypoints)

        # PATRULLA 1: Guardia horizontal (ida y vuelta rápida)
        # Usa los primeros 2 waypoints
        if num_waypoints >= 2:
            path1 = [self.waypoints[0], self.waypoints[1]]
            enemy1 = PatrolEnemy(path1, speed=3.0)
            self.enemies.append(enemy1)
            self.add_widget(enemy1)

        # PATRULLA 2: Recorrido vertical lento (más predecible)
        # Usa waypoints intermedios
        if num_waypoints >= 3:
            path2 = [self.waypoints[1], self.waypoints[2]]
            enemy2 = PatrolEnemy(path2, speed=1.8)
            self.enemies.append(enemy2)
            self.add_widget(enemy2)

        # PATRULLA 3: Triángulo (patrulla táctica)
        # Crea un patrón triangular si hay suficientes waypoints
        if num_waypoints >= 4:
            path3 = [
                self.waypoints[0],
                self.waypoints[2],
                self.waypoints[3],
            ]
            enemy3 = PatrolEnemy(path3, speed=2.5)
            self.enemies.append(enemy3)
            self.add_widget(enemy3)

        # PATRULLA 4: Recorrido completo (difícil de predecir)
        # Usa todos los waypoints disponibles
        if num_waypoints >= 5:
            path4 = [
                self.waypoints[0],
                self.waypoints[2],
                self.waypoints[4],
                self.waypoints[3],
                self.waypoints[1],
            ]
            enemy4 = PatrolEnemy(path4, speed=2.2)
            self.enemies.append(enemy4)
            self.add_widget(enemy4)

        # PATRULLA 5: Guardia de área (cuadrado/rectángulo)
        # Patrulla cubriendo un área específica
        if num_waypoints >= 5:
            path5 = [
                self.waypoints[1],
                self.waypoints[3],
                self.waypoints[4],
                self.waypoints[2],
            ]
            enemy5 = PatrolEnemy(path5, speed=2.0)
            self.enemies.append(enemy5)
            self.add_widget(enemy5)

        # PATRULLA 6: Centinela rápido (patrulla corta y ágil)
        # Enemigo difícil de golpear
        if num_waypoints >= 4:
            path6 = [self.waypoints[2], self.waypoints[3]]
            enemy6 = PatrolEnemy(path6, speed=3.5)
            self.enemies.append(enemy6)
            self.add_widget(enemy6)

        # PATRULLA 7: Ronda larga (supervisor)
        # Enemigo que recorre todo el perímetro
        if num_waypoints >= 5:
            # Crear una ruta que conecte los waypoints exteriores
            path7 = self.waypoints[:] if num_waypoints <= 6 else self.waypoints[:6]
            enemy7 = PatrolEnemy(path7, speed=1.5)
            self.enemies.append(enemy7)
            self.add_widget(enemy7)

        # PATRULLA 8: Zigzag (patrón impredecible)
        # Alterna entre waypoints para crear movimiento errático
        if num_waypoints >= 5:
            path8 = [
                self.waypoints[0],
                self.waypoints[4],
                self.waypoints[1],
                self.waypoints[3],
            ]
            enemy8 = PatrolEnemy(path8, speed=2.8)
            self.enemies.append(enemy8)
            self.add_widget(enemy8)

    # =====================================================
    # EVENTOS DE TOUCH
    # =====================================================
    def on_touch_down(self, touch):
        if self.player.collide_point(*touch.pos):
            self.is_dragging = True
            self.drag_start = self.player.center
            self.player.set_dragging(True)
            self.trajectory.show()
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.is_dragging:
            return super().on_touch_move(touch)

        sx, sy = self.drag_start
        tx, ty = touch.pos
        dx = tx - sx
        dy = ty - sy

        vx = -dx
        vy = -dy

        drag_dist = hypot(dx, dy)
        if drag_dist > self.max_drag_distance and drag_dist > 0:
            scale = self.max_drag_distance / drag_dist
            vx *= scale
            vy *= scale

        self.current_force = (vx * self.launch_power, vy * self.launch_power)
        self.trajectory.update_dots(self.drag_start, self.current_force)
        return True

    def on_touch_up(self, touch):
        if not self.is_dragging:
            return super().on_touch_up(touch)

        self.is_dragging = False
        self.player.set_dragging(False)
        self.trajectory.hide()
        self.spawn_projectile(self.current_force)
        self.current_force = (0.0, 0.0)
        self.drag_start = None
        return True

    # =====================================================
    # LÓGICA DE DISPARO
    # =====================================================
    def spawn_projectile(self, velocity: Tuple[float, float]):
        proj = PhysicsProjectile(source="images/huevo.png")
        proj.size_hint = (None, None)
        proj.size = (38, 38)
        proj.center = self.player.center
        proj.gravity = -150.0
        proj.velocity_x = float(velocity[0])
        proj.velocity_y = float(velocity[1])
        self.add_widget(proj)
        self.projectiles.append(proj)

    # =====================================================
    # UPDATE GENERAL
    # =====================================================
    def update(self, dt: float):
        # Actualizar proyectiles
        for proj in self.projectiles[:]:
            proj.update_with_walls(dt, self.wall_rects, on_impact=self.on_projectile_impact)
            if not proj.alive:
                if proj.parent:
                    self.remove_widget(proj)
                self.projectiles.remove(proj)
                continue

            # Colisiones con enemigos
            for enemy in self.enemies[:]:
                if getattr(enemy, "is_dead", False):
                    continue
                if self.check_collision(proj, enemy):
                    # eliminar enemigo y proyectil
                    if hasattr(enemy, "destroy"):
                        enemy.destroy()
                    else:
                        self.remove_widget(enemy)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

                    proj.alive = False
                    if proj.parent:
                        self.remove_widget(proj)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    break

        # limpiar enemigos muertos (tras animación)
        for enemy in self.enemies[:]:
            if getattr(enemy, "is_dead", False):
                try:
                    if enemy.sprite.opacity <= 0.02:
                        self.remove_widget(enemy)
                        self.enemies.remove(enemy)
                except Exception:
                    pass

    # =====================================================
    # COLISIÓN ENTRE PROYECTIL Y ENEMIGO
    # =====================================================
    def check_collision(self, proj: PhysicsProjectile, enemy: Widget) -> bool:
        try:
            px, py = proj.center
            ex, ey = enemy.center
            pr = proj.width / 2
            er = getattr(enemy.sprite, "width", 80) / 2 * 0.8
            dist = sqrt((px - ex) ** 2 + (py - ey) ** 2)
            return dist < (pr + er)
        except Exception:
            return False

    def on_projectile_impact(self, x: float, y: float):
        # futuro: explosión o efecto visual
        pass

    # =====================================================
    # AJUSTE DE FONDO AL CAMBIO DE VENTANA
    # =====================================================
    def on_size(self, *args):
        if hasattr(self, "bg"):
            self.bg.size = (self.width, self.height)
            self.bg.pos = (0, 0)