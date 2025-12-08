# game/trajectory_screen.py

from typing import List, Optional, Tuple
from math import hypot, sqrt

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Rectangle , Color, RoundedRectangle
from kivy.clock import Clock
from kivy.uix.label import Label            # <-- NUEVO
from kivy.uix.button import Button 
# Tus clases
from game.slingshot_player import SlingshotPlayer
from game.trajectory import Trajectory
from game.physics_projectile import PhysicsProjectile
from game.level1 import Level1Spec
from game.enemy_patrol import PatrolEnemy

DEBUG_HUD = True

DIFFICULTY_PRESETS = {
    "easy":   {"attempts": 12, "time_limit": 90, "enemy_speed_scale": 0.9},
    "normal": {"attempts": 10, "time_limit": 75, "enemy_speed_scale": 1.0},
    "hard":   {"attempts": 8,  "time_limit": 60, "enemy_speed_scale": 1.2},  # 8 intentos (8 enemigos)
}

HUD_WIDTH = 420
HUD_HEIGHT = 50
HUD_MARGIN_TOP = 8


class TrajectoryGameScreen(Widget):
    """
    Nivel 1: el jugador lanza proyectiles (huevos) con una resortera.
    El proyectil cae por gravedad, choca contra paredes y puede
    destruir enemigos que patrullan usando los waypoints del nivel.
    """

    def __init__(self, difficulty: str = "normal", **kwargs):
        super().__init__(**kwargs)
        self.difficulty = difficulty if difficulty in DIFFICULTY_PRESETS else "normal"
        self.config = DIFFICULTY_PRESETS[self.difficulty]
        # -------------------------------------------------
        # 1) Fondo
        # -------------------------------------------------
        # Asegurar tamaño y reactividad a cambios de ventana
        self.size = Window.size
        
        
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1) # Para poder cambiar opacidad
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
        # 6.1) Intentos/tiempo HUD
        # -------------------------------------------------
        self.attempts_left: int = int(self.config["attempts"])
        self.time_left: float = float(self.config["time_limit"])
        self.finished: bool = False

        # Panel de fondo del HUD
        self.hud_panel = Widget()
        self.add_widget(self.hud_panel)
        with self.hud_panel.canvas.before:
            Color(0.06, 0.08, 0.12, 0.9)  # fondo oscuro semi-transparente
            self.hud_bg = RoundedRectangle(pos=(0, 0), size=(1, 1), radius=[12])

        # Borde rojo para depurar área del HUD
        if DEBUG_HUD:
            with self.hud_panel.canvas.after:
                Color(1, 0, 0, 0.35)
                self._hud_dbg = Rectangle(pos=(0, 0), size=(1, 1))

        self.hud = Label(
            text=self._hud_text(),
            font_size="22sp",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            halign="center",
            valign="middle",
            markup=True,
        )
        self.add_widget(self.hud)
        
        self._layout_hud()
        self.bind(size=lambda *_: self._layout_hud())
        Window.bind(size=lambda *_: self._layout_hud())
        Clock.schedule_once(lambda dt: self._layout_hud(), 0)
        if DEBUG_HUD:
            print("[HUD] creado")
        # -------------------------------------------------
        # 7) Crear enemigos que patrullan los waypoints
        # -------------------------------------------------
        self.spawn_patrol_enemies(speed_scale=float(self.config["enemy_speed_scale"]))

        # -------------------------------------------------
        # 8) Bucle de juego
        # -------------------------------------------------
        Clock.schedule_interval(self.update, 1 / 60)
        Window.bind(size=lambda *_: self._on_window_resize())
        self._raise_hud_to_top()
    
    # HUD helpers -------------------------------------------------------------
    def _on_window_resize(self):
        # Ajustar fondo y HUD cuando cambie la ventana
        if hasattr(self, "bg"):
            self.bg.size = (Window.width, Window.height)
            self.bg.pos = (0, 0)
        self._layout_hud()

    def _layout_hud(self, *args):
        if not hasattr(self, "hud_bg") or not hasattr(self, "hud"):
            return
        # { changed code } tamaño fijo y centrado horizontal con margen superior constante
        panel_w = HUD_WIDTH
        panel_h = HUD_HEIGHT
        px = (Window.width - panel_w) / 2
        py = Window.height - panel_h - HUD_MARGIN_TOP

        # fondo
        self.hud_bg.pos = (px, py)
        self.hud_bg.size = (panel_w, panel_h)

        # texto
        self.hud.size = (panel_w, panel_h)
        self.hud.text_size = (panel_w, panel_h)
        self.hud.pos = (px, py)

        if DEBUG_HUD and hasattr(self, "_hud_dbg"):
            self._hud_dbg.pos = (px, py)
            self._hud_dbg.size = (panel_w, panel_h)

    def _raise_hud_to_top(self):
        # Reinsertar para que quede arriba de todo
        if self.hud_panel.parent:
            self.remove_widget(self.hud_panel)
        if self.hud.parent:
            self.remove_widget(self.hud)
        self.add_widget(self.hud_panel)
        self.add_widget(self.hud)
    if DEBUG_HUD:
            print("[HUD] raised to top")
    # NUEVO: texto HUD
    def _hud_text(self) -> str:
        t = int(max(0, self.time_left))
        return f"[b]Intentos:[/b] {self.attempts_left} [b]Tiempo:[/b] {t}s"
    
    # =====================================================
    # CREACIÓN DE ENEMIGOS MEJORADA
    # =====================================================
    def spawn_patrol_enemies(self, speed_scale: float = 1.0):
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
            enemy1 = PatrolEnemy(path1, speed=3.0 * speed_scale)
            self.enemies.append(enemy1)
            self.add_widget(enemy1)

        # PATRULLA 2: Recorrido vertical lento (más predecible)
        # Usa waypoints intermedios
        if num_waypoints >= 3:
            path2 = [self.waypoints[1], self.waypoints[2]]
            enemy2 = PatrolEnemy(path2, speed=1.8 * speed_scale)
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
            enemy3 = PatrolEnemy(path3, speed=2.5 * speed_scale)
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
            enemy4 = PatrolEnemy(path4, speed=2.2 * speed_scale)
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
            enemy5 = PatrolEnemy(path5, speed=2.0 * speed_scale)
            self.enemies.append(enemy5)
            self.add_widget(enemy5)

        # PATRULLA 6: Centinela rápido (patrulla corta y ágil)
        # Enemigo difícil de golpear
        if num_waypoints >= 4:
            path6 = [self.waypoints[2], self.waypoints[3]]
            enemy6 = PatrolEnemy(path6, speed=3.5 * speed_scale)
            self.enemies.append(enemy6)
            self.add_widget(enemy6)

        # PATRULLA 7: Ronda larga (supervisor)
        # Enemigo que recorre todo el perímetro
        if num_waypoints >= 5:
            # Crear una ruta que conecte los waypoints exteriores
            path7 = self.waypoints[:] if num_waypoints <= 6 else self.waypoints[:6]
            enemy7 = PatrolEnemy(path7, speed=1.5 * speed_scale)
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
            enemy8 = PatrolEnemy(path8, speed=2.8 * speed_scale)
            self.enemies.append(enemy8)
            self.add_widget(enemy8)

    # =====================================================
    # EVENTOS DE TOUCH
    # =====================================================
    def on_touch_down(self, touch):
        if self.finished:
            return super().on_touch_down(touch)
        # No iniciar si ya no quedan intentos
        if self.attempts_left <= 0:
            return True
        
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
        # Consumir intento y disparar solo si quedan
        if self.attempts_left > 0 and not self.finished:
            self.spawn_projectile(self.current_force)
            self.attempts_left -= 1
            self.hud.text = self._hud_text()
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
        proj.life = 0.0
        self._raise_hud_to_top()
        if DEBUG_HUD:
            print(f"[HUD] projectile spawned; attempts_left={self.attempts_left}")

    # =====================================================
    # UPDATE GENERAL
    # =====================================================
    def update(self, dt: float):

        if self.finished:
            return

        # Tiempo límite
        self.time_left -= dt
        if self.time_left < 0:
            self.time_left = 0

        self.hud.text = self._hud_text()

        # Actualizar proyectiles
        for proj in self.projectiles[:]:
            proj.update_with_walls(dt, self.wall_rects, on_impact=self.on_projectile_impact)
            self._cull_projectile(proj, dt)
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
        # Condiciones de fin:
        all_enemies_down = (len(self.enemies) == 0)
        no_more_attempts = (self.attempts_left <= 0)
        no_active_projectiles = (len(self.projectiles) == 0)

        if all_enemies_down:
            self.finish_level(won=True)
            return
        # Se acabó el tiempo y no mataste a todos
        if self.time_left <= 0 and not all_enemies_down:
            self.finish_level(won=False)
            return
        # Se acabaron los intentos y ya no hay proyectiles en vuelo
        if no_more_attempts and no_active_projectiles:
            self.finish_level(won=False)
            return
        
    # --- NUEVO: helper para “matar” proyectiles atascados ---
    def _cull_projectile(self, proj: PhysicsProjectile, dt: float):
        # TTL: elimina el proyectil después de 6s (o 3s si ya no quedan intentos)
        if not hasattr(proj, "life"):
            proj.life = 0.0
        proj.life += dt
        ttl = 6.0 if self.attempts_left > 0 else 3.0
        # Fuera de pantalla
        out = (
            proj.x < -80 or proj.right > Window.width + 80 or
            proj.top < -80 or proj.y > Window.height + 80
        )
        if out or proj.life > ttl:
            proj.alive = False
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
        if hasattr(self, "hud_bg"):
            self._layout_hud()
    
    # { changed code } Overlay de fin más visible con fondo y botones
    def finish_level(self, won: bool):
        if self.finished:
            return
        self.finished = True

        # Detener lógica inmediatamente
        try:
            Clock.unschedule(self.update)
        except Exception:
            pass

        self._raise_hud_to_top()

        # Fondo semi-transparente
        overlay = Widget()
        with overlay.canvas.before:
            Color(0, 0, 0, 0.65)
            Rectangle(size=(Window.width, Window.height), pos=(0, 0))

        # Panel central
        panel_w, panel_h = 420, 280
        panel_x, panel_y = Window.width/2 - panel_w/2, Window.height/2 - panel_h/2
        with overlay.canvas:
            Color(0.12, 0.14, 0.18, 0.98)
            RoundedRectangle(pos=(panel_x, panel_y), size=(panel_w, panel_h), radius=[20])

        title = "¡Victoria!" if won else "Has perdido"
        lbl = Label(
            text=f"[b]{title}[/b]\nIntentos: {self.attempts_left}   Tiempo: {int(self.time_left)}s",
            markup=True, font_size="22sp",
            size_hint=(None, None),
            pos=(0, panel_y + panel_h - 80),
            width=Window.width, halign="center"
        )
        self.add_widget(overlay)
        self.add_widget(lbl)

        btn_retry = Button(text="Reintentar", size_hint=(None, None), size=(160, 56),
                           pos=(Window.width/2 - 180, panel_y + 30))
        btn_menu  = Button(text="Menú", size_hint=(None, None), size=(160, 56),
                           pos=(Window.width/2 + 20, panel_y + 30))
        btn_retry.bind(on_press=lambda *_: self.restart_level())
        btn_menu.bind(on_press=lambda *_: self.go_to_menu())
        self.add_widget(btn_retry)
        self.add_widget(btn_menu)

    def restart_level(self):
        from kivy.app import App
        App.get_running_app().start_level2(self.difficulty)

    def go_to_menu(self):
        from kivy.app import App
        App.get_running_app().show_main_menu()