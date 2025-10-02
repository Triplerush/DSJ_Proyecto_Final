from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App
from kivy.graphics import Rectangle
from kivy.core.window import Window
import math, random

from game.player import Player
from game.enemy import Enemy
from game.projectile import Projectile
from game.overlays import PauseMenu, GameOverMenu, PauseButton


class GameScreen(Widget):
    score = NumericProperty(0)
    score_text = StringProperty("Score: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Estado del juego
        self.is_paused = False
        self.game_over = False

        # --- Lógica de fondo con scrolling ---
        IMG_WIDTH = 2304
        IMG_HEIGHT = 1024
        SCROLL_DURATION = 60

        aspect_ratio = IMG_WIDTH / IMG_HEIGHT
        self.scaled_bg_height = Window.height
        self.scaled_bg_width = self.scaled_bg_height * aspect_ratio

        scroll_distance = self.scaled_bg_width - Window.width
        self.scroll_speed = scroll_distance / SCROLL_DURATION

        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo1.png",
                size=(self.scaled_bg_width, self.scaled_bg_height),
                pos=(0, 0)
            )

        self.player = Player()
        self.add_widget(self.player)

        self.enemies = []
        self.projectiles = []

        # Label de puntuación
        self.label = Label(text=self.score_text,
                           font_size='24sp',
                           color=(1, 1, 1, 1),
                           size_hint=(0.3, 0.1),
                           pos_hint={'x': 0.02, 'top': 0.98},
                           halign="left", valign="top")
        self.add_widget(self.label)

        # Botón de pausa
        self.pause_button = PauseButton()
        self.pause_button.bind(on_press=lambda x: self.toggle_pause())
        self.add_widget(self.pause_button)

        # Eventos programados
        self.spawn_event = Clock.schedule_interval(self.spawn_enemy, 2)
        self.update_event = Clock.schedule_interval(self.update, 1 / 60)
        self.score_event = Clock.schedule_interval(self.add_score, 1)

        # Overlays (inicialmente None)
        self.pause_menu = None
        self.gameover_menu = None

        # Vincular tecla ESC para pausar
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Maneja eventos de teclado"""
        if key == 27:  # ESC
            if not self.game_over:
                self.toggle_pause()
            return True
        return False

    def toggle_pause(self):
        """Alternar pausa del juego"""
        if self.game_over:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            # Pausar el juego
            self.spawn_event.cancel()
            self.update_event.cancel()
            self.score_event.cancel()
            
            # Mostrar menú de pausa
            self.pause_menu = PauseMenu(self)
            self.add_widget(self.pause_menu)
            
            # Cambiar icono del botón
            self.pause_button.text = "▶"
        else:
            # Reanudar el juego
            self.spawn_event = Clock.schedule_interval(self.spawn_enemy, 2)
            self.update_event = Clock.schedule_interval(self.update, 1 / 60)
            self.score_event = Clock.schedule_interval(self.add_score, 1)
            
            # Ocultar menú de pausa
            if self.pause_menu:
                self.remove_widget(self.pause_menu)
                self.pause_menu = None
            
            # Restaurar icono del botón
            self.pause_button.text = "⏸"

    def show_game_over(self):
        """Mostrar pantalla de Game Over"""
        self.game_over = True
        
        # Detener todos los eventos
        self.spawn_event.cancel()
        self.update_event.cancel()
        self.score_event.cancel()
        
        # Mostrar menú de game over
        self.gameover_menu = GameOverMenu(self, self.score)
        self.add_widget(self.gameover_menu)
        
        # Ocultar botón de pausa
        self.pause_button.opacity = 0

    def restart_game(self):
        """Reiniciar el juego"""
        # Obtener referencia a la app
        app = App.get_running_app()
        app.start_game()

    def go_to_main_menu(self):
        """Volver al menú principal"""
        app = App.get_running_app()
        app.show_main_menu()

    def spawn_enemy(self, dt):
        if self.is_paused or self.game_over:
            return

        homing_count = sum(1 for e in self.enemies if e.is_homing)

        is_homing = False
        if homing_count < 5 and random.random() < 0.3:
            is_homing = True

        enemy = Enemy(self.player, is_homing=is_homing)
        
        def shoot_for_this_enemy():
            self.create_projectile(enemy)
        
        enemy.shoot_projectile = shoot_for_this_enemy

        max_attempts = 10
        attempts = 0
        while attempts < max_attempts and any(self.check_enemy_overlap(enemy, other) for other in self.enemies):
            enemy.center_x = random.randint(50, self.width - 50)
            attempts += 1

        self.enemies.append(enemy)
        self.add_widget(enemy)

    def create_projectile(self, enemy):
        if enemy not in self.enemies:
            return
            
        projectile = Projectile(
            start_x=enemy.center_x,
            start_y=enemy.center_y,
            target_x=self.player.center_x,
            target_y=self.player.center_y
        )
        self.projectiles.append(projectile)
        self.add_widget(projectile)

    def update(self, dt):
        if self.is_paused or self.game_over:
            return

        # Mover el fondo
        left_limit = -(self.scaled_bg_width - Window.width)
        new_x = self.bg.pos[0] - self.scroll_speed * dt
        
        if new_x > left_limit:
            self.bg.pos = (new_x, 0)
        
        # Actualizar enemigos
        for enemy in self.enemies[:]:
            alive = enemy.update(dt)

            if not alive:
                self.remove_widget(enemy)
                self.enemies.remove(enemy)
                continue

            if self.check_collision(self.player, enemy):
                print("¡Perdiste! Colisión con enemigo")
                self.show_game_over()
                return

        # Actualizar proyectiles
        for projectile in self.projectiles[:]:
            alive = projectile.update(dt)
            
            if not alive:
                self.remove_widget(projectile)
                self.projectiles.remove(projectile)
                continue
            
            if self.check_projectile_collision(self.player, projectile):
                print("¡Perdiste! Colisión con proyectil")
                self.show_game_over()
                return

        self.label.text = self.score_text

    def add_score(self, dt):
        if self.is_paused or self.game_over:
            return
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
        if self.is_paused or self.game_over:
            return super().on_touch_down(touch)
        
        # Verificar si tocó el botón de pausa
        if self.pause_button.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        
        self.player.move_to(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_paused or self.game_over:
            return super().on_touch_move(touch)
        
        self.player.move_to(touch)
        return super().on_touch_move(touch)
