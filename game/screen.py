from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App
from kivy.graphics import Rectangle
from kivy.core.window import Window
import math, random

from .player import Player
from .enemy import Enemy
from .projectile import Projectile


class GameScreen(Widget):
    score = NumericProperty(0)
    score_text = StringProperty("Score: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # --- Lógica de fondo con scrolling ---
        # Dimensiones originales de tu imagen de fondo
        IMG_WIDTH = 2304
        IMG_HEIGHT = 1024
        SCROLL_DURATION = 60  # segundos para el recorrido completo

        # Calcular el tamaño del fondo manteniendo la proporción
        aspect_ratio = IMG_WIDTH / IMG_HEIGHT
        self.scaled_bg_height = Window.height
        self.scaled_bg_width = self.scaled_bg_height * aspect_ratio

        # Calcular la distancia y velocidad del scroll
        scroll_distance = self.scaled_bg_width - Window.width
        self.scroll_speed = scroll_distance / SCROLL_DURATION

        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo1.png",
                size=(self.scaled_bg_width, self.scaled_bg_height),
                pos=(0, 0)
            )
        # --------------------------------------------------------

        self.player = Player()
        self.add_widget(self.player)

        self.enemies = []
        self.projectiles = []  # Lista de proyectiles

        # Label de puntuación
        self.label = Label(text=self.score_text,
                           font_size='24sp',
                           color=(1, 1, 1, 1),
                           size_hint=(0.3, 0.1),
                           pos_hint={'x': 0.02, 'top': 0.98},
                           halign="left", valign="top")
        self.add_widget(self.label)

        Clock.schedule_interval(self.spawn_enemy, 2)
        Clock.schedule_interval(self.update, 1 / 60)
        Clock.schedule_interval(self.add_score, 1)

    def spawn_enemy(self, dt):
        # Contar cuántos homing existen
        homing_count = sum(1 for e in self.enemies if e.is_homing)

        # 30% chance de homing pero máximo 5
        is_homing = False
        if homing_count < 5 and random.random() < 0.3:
            is_homing = True

        enemy = Enemy(self.player, is_homing=is_homing)
        
        # Configurar el método de disparo para este enemigo específico
        def shoot_for_this_enemy():
            self.create_projectile(enemy)
        
        enemy.shoot_projectile = shoot_for_this_enemy

        # Evitar superposición con otros enemigos
        max_attempts = 10
        attempts = 0
        while attempts < max_attempts and any(self.check_enemy_overlap(enemy, other) for other in self.enemies):
            enemy.center_x = random.randint(50, self.width - 50)
            attempts += 1

        self.enemies.append(enemy)
        self.add_widget(enemy)

    def create_projectile(self, enemy):
        """Crear un proyectil desde un enemigo hacia el jugador"""
        # Debug: verificar que el enemigo existe
        if enemy not in self.enemies:
            return
            
        # Crear proyectil con las posiciones actuales
        projectile = Projectile(
            start_x=enemy.center_x,
            start_y=enemy.center_y,
            target_x=self.player.center_x,
            target_y=self.player.center_y
        )
        # Agregar a la lista de proyectiles
        self.projectiles.append(projectile)
        # IMPORTANTE: Agregar el proyectil al GameScreen, NO al enemy
        self.add_widget(projectile)
        print(f"Proyectil creado en ({enemy.center_x}, {enemy.center_y})")

    def update(self, dt):
        # --- Mover el fondo ---
        # Calculamos el límite izquierdo para detener el scroll
        left_limit = -(self.scaled_bg_width - Window.width)
        
        # Nueva posición x
        new_x = self.bg.pos[0] - self.scroll_speed * dt
        
        # Nos aseguramos de no pasar del límite
        if new_x > left_limit:
            self.bg.pos = (new_x, 0)
        # ------------------------------------
        
        # Actualizar enemigos (usar copia de la lista)
        for enemy in self.enemies[:]:
            alive = enemy.update(dt)

            if not alive:
                self.remove_widget(enemy)
                self.enemies.remove(enemy)
                continue

            if self.check_collision(self.player, enemy):
                print("¡Perdiste! Colisión con enemigo")
                App.get_running_app().stop()
                return

        # Actualizar proyectiles (usar copia de la lista)
        for projectile in self.projectiles[:]:
            alive = projectile.update(dt)
            
            if not alive:
                self.remove_widget(projectile)
                self.projectiles.remove(projectile)
                continue
            
            # Verificar colisión con el jugador
            if self.check_projectile_collision(self.player, projectile):
                print("¡Perdiste! Colisión con proyectil")
                App.get_running_app().stop()
                return

        self.label.text = self.score_text

    def add_score(self, dt):
        self.score += 1
        self.score_text = f"Score: {self.score}"

    def check_collision(self, player, enemy):
        px, py = player.center_x, player.center_y
        ex, ey = enemy.center_x, enemy.center_y

        pr = player.sprite.width / 2 * 0.8
        er = enemy.sprite.width / 2 * 0.8

        distancia = math.sqrt((px - ex)**2 + (py - ey)**2)
        return distancia < (pr + er)

    def check_projectile_collision(self, player, projectile):
        """Verificar colisión entre el jugador y un proyectil"""
        px, py = player.center_x, player.center_y
        proj_x, proj_y = projectile.center_x, projectile.center_y

        pr = player.sprite.width / 2 * 0.7
        proj_r = projectile.sprite.width / 2

        distancia = math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
        return distancia < (pr + proj_r)

    def check_enemy_overlap(self, e1, e2):
        ex1, ey1 = e1.center_x, e1.center_y
        ex2, ey2 = e2.center_x, e2.center_y
        r = e1.sprite.width / 2
        distancia = math.sqrt((ex1 - ex2)**2 + (ey1 - ey2)**2)
        return distancia < r * 1.5

    def on_touch_down(self, touch):
        self.player.move_to(touch)

    def on_touch_move(self, touch):
        self.player.move_to(touch)