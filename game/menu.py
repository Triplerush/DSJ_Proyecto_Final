from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color, RoundedRectangle, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout           # <-- FALTABAN ESTOS IMPORTS
from kivy.uix.popup import Popup 
from kivy.uix.gridlayout import GridLayout  # NUEVO

import random


class MenuButton(Button):
    """Botón personalizado para el menú con efectos mejorados"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Transparente para usar canvas
        self.background_normal = ''
        self.font_size = '24sp'
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.size = (320, 65)
        
        # Dibujar fondo personalizado
        with self.canvas.before:
            self.bg_color = Color(0.15, 0.5, 0.85, 0.9)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15]
            )
            # Borde brillante
            self.border_color = Color(0.3, 0.7, 1, 0.6)
            self.border_rect = RoundedRectangle(
                pos=(self.pos[0] - 2, self.pos[1] - 2),
                size=(self.size[0] + 4, self.size[1] + 4),
                radius=[15]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
    
    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0] - 2, self.pos[1] - 2)
        self.border_rect.size = (self.size[0] + 4, self.size[1] + 4)
    
    def on_button_press(self, instance):
        """Animación al presionar el botón"""
        self.bg_color.rgba = (0.1, 0.4, 0.7, 1)
        anim = Animation(size=(330, 70), duration=0.1)
        anim.start(self)
    
    def on_button_release(self, instance):
        """Restaurar animación"""
        self.bg_color.rgba = (0.15, 0.5, 0.85, 0.9)
        anim = Animation(size=(320, 65), duration=0.1)
        anim.start(self)


class ExitButton(Button):
    """Botón especial para salir"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.font_size = '22sp'
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.size = (320, 60)
        
        with self.canvas.before:
            self.bg_color = Color(0.8, 0.2, 0.2, 0.85)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15]
            )
            self.border_color = Color(1, 0.3, 0.3, 0.6)
            self.border_rect = RoundedRectangle(
                pos=(self.pos[0] - 2, self.pos[1] - 2),
                size=(self.size[0] + 4, self.size[1] + 4),
                radius=[15]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
    
    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0] - 2, self.pos[1] - 2)
        self.border_rect.size = (self.size[0] + 4, self.size[1] + 4)
    
    def on_button_press(self, instance):
        self.bg_color.rgba = (0.6, 0.15, 0.15, 1)
        anim = Animation(size=(330, 65), duration=0.1)
        anim.start(self)
    
    def on_button_release(self, instance):
        self.bg_color.rgba = (0.8, 0.2, 0.2, 0.85)
        anim = Animation(size=(320, 60), duration=0.1)
        anim.start(self)


class MainMenu(Widget):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        # Fondo del menú con efecto
        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo1.png",
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
            # Overlay con gradiente oscuro
            Color(0, 0, 0, 0.55)
            self.overlay = Rectangle(
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
        
        # Título del juego con sombra
        self.title_shadow = Label(
            text="[b]EL VUELO DEL CÓNDOR[/b]",
            markup=True,
            font_size='52sp',
            color=(0, 0, 0, 0.5),
            size_hint=(None, None),
            size=(Window.width, 100),
            pos=(3, Window.height - 177)
        )
        self.add_widget(self.title_shadow)
        
        self.title = Label(
            text="[b]EL VUELO DEL CÓNDOR[/b]",
            markup=True,
            font_size='52sp',
            color=(1, 0.9, 0.2, 1),
            size_hint=(None, None),
            size=(Window.width, 100),
            pos=(0, Window.height - 180)
        )
        self.add_widget(self.title)
        
        # Subtítulo
        self.subtitle = Label(
            text="[i]Una Aventura en los Andes[/i]",
            markup=True,
            font_size='20sp',
            color=(0.9, 0.9, 0.9, 0.8),
            size_hint=(None, None),
            size=(Window.width, 40),
            pos=(0, Window.height - 220)
        )
        self.add_widget(self.subtitle)
        
        # Animación del título
        self.animate_title()
        
        # Sprites animados decorativos (jugador)
        self.player_sprites = []
        self.animation_frames_player = [
            "images/ave1.png",
            "images/ave2.png",
            "images/ave3.png",
            "images/ave4.png"
        ]
        self.current_frame_player = 0
        
        for i in range(2):
            sprite = Image(
                source=self.animation_frames_player[0],
                size_hint=(None, None),
                size=(110, 110),
                pos=(30 + i * (Window.width - 140), Window.height - 320)
            )
            self.add_widget(sprite)
            self.player_sprites.append(sprite)
        
        # Sprites animados decorativos (enemigos)
        self.enemy_sprites = []
        self.animation_frames_enemy = [
            "images/enemigo1.png",
            "images/enemigo2.png",
            "images/enemigo3.png",
            "images/enemigo4.png"
        ]
        self.current_frame_enemy = 0
        
        for i in range(3):
            sprite = Image(
                source=self.animation_frames_enemy[0],
                size_hint=(None, None),
                size=(85, 85),
                pos=(80 + i * 180, 90)
            )
            self.add_widget(sprite)
            self.enemy_sprites.append(sprite)
        
        # Iniciar animaciones de sprites
        Clock.schedule_interval(self.animate_sprites, 0.15)
        
        # Botones del menú con mejor espaciado
        button_y = Window.height / 2 + 80
        button_spacing = 80
        
        # Botón Jugar
        self.play_button = MenuButton(text="JUGAR")
        self.play_button.pos = (Window.width / 2 - 160, button_y)
        self.play_button.bind(on_press=lambda *_: self.open_level_select())
        self.add_widget(self.play_button)
        
        # Botón Instrucciones
        self.instructions_button = MenuButton(text="INSTRUCCIONES")
        self.instructions_button.pos = (Window.width / 2 - 160, button_y - button_spacing * 2)
        self.instructions_button.bind(on_press=self.show_instructions)
        self.add_widget(self.instructions_button)
        
        # Botón Salir
        self.exit_button = ExitButton(text="SALIR")
        self.exit_button.pos = (Window.width / 2 - 160, button_y - button_spacing * 4)
        self.exit_button.bind(on_press=self.exit_game)
        self.add_widget(self.exit_button)
        
        # Versión del juego mejorada
        self.version_label = Label(
            text="[b]Versión 1.0[/b]",
            markup=True,
            font_size='16sp',
            color=(1, 1, 1, 0.7),
            size_hint=(None, None),
            size=(120, 30),
            pos=(Window.width - 130, 15)
        )
        self.add_widget(self.version_label)
    
    def animate_title(self):
        """Animación pulsante del título mejorada"""
        anim = (Animation(font_size=56, duration=1.2) +
                Animation(font_size=52, duration=1.2))
        anim.repeat = True
        anim.start(self.title)
        
        # Animar también la sombra
        anim_shadow = (Animation(font_size=58, duration=1.2) +
                       Animation(font_size=54, duration=1.2))
        anim_shadow.repeat = True
        anim_shadow.start(self.title_shadow)
    
    def animate_sprites(self, dt):
        """Anima los sprites decorativos"""
        # Animar jugadores
        self.current_frame_player = (self.current_frame_player + 1) % len(self.animation_frames_player)
        for sprite in self.player_sprites:
            sprite.source = self.animation_frames_player[self.current_frame_player]
        
        # Animar enemigos
        self.current_frame_enemy = (self.current_frame_enemy + 1) % len(self.animation_frames_enemy)
        for sprite in self.enemy_sprites:
            sprite.source = self.animation_frames_enemy[self.current_frame_enemy]
    
    def start_game(self, instance):
        """Inicia el juego"""
        print("Iniciando juego...")
        self.app.start_game()
    
    def show_levels(self, instance):
        """Muestra pantalla de selección de niveles"""
        print("Mostrando niveles...")
        self.app.show_level_screen()
    
    def show_instructions(self, instance):
        """Muestra las instrucciones"""
        print("Mostrando instrucciones...")
        self.app.show_instructions_screen()
    
    def show_options(self, instance):
        """Muestra las opciones (por implementar)"""
        print("Opciones - Próximamente...")
    
    def exit_game(self, instance):
        """Cierra la aplicación"""
        print("Saliendo del juego...")
        App.get_running_app().stop()

    def open_level_select(self):
        content = BoxLayout(orientation='vertical', spacing=12, padding=(20,20,20,20))
        lbl = Label(text="[b]Selecciona Nivel[/b]", markup=True, size_hint=(1, None), height=42)
        content.add_widget(lbl)

        grid = GridLayout(cols=1, spacing=10, size_hint=(1, None))
        grid.bind(minimum_height=grid.setter('height'))
        btn_n1 = MenuButton(text="NIVEL 1", size_hint=(1, None), height=56)
        btn_n2 = MenuButton(text="NIVEL 2", size_hint=(1, None), height=56)
        grid.add_widget(btn_n1)
        grid.add_widget(btn_n2)
        content.add_widget(grid)

        btn_cancel = ExitButton(text="CANCELAR", size_hint=(1, None), height=52)
        content.add_widget(btn_cancel)

        popup = Popup(title="Seleccionar Nivel", content=content,
                      size_hint=(None, None), size=(410, 270), auto_dismiss=True)
        popup.separator_color = (0, 0, 0, 0)
        btn_n1.bind(on_press=lambda *_: (popup.dismiss(), self.start_level1()))
        btn_n2.bind(on_press=lambda *_: (popup.dismiss(), self.open_difficulty_select()))
        btn_cancel.bind(on_press=lambda *_: popup.dismiss())
        popup.open()

    def start_level1(self):
        if self.app and hasattr(self.app, "start_level1"):
            self.app.start_level1()
    
    def open_difficulty_select(self):
        content = BoxLayout(orientation='vertical', spacing=12, padding=(20,20,20,20))
        lbl = Label(text="[b]Nivel 2 - Selecciona Dificultad[/b]\nFácil, Normal o Difícil",
                    markup=True, size_hint=(1, None), height=68)
        content.add_widget(lbl)

        grid = GridLayout(cols=1, spacing=10, size_hint=(1, None))
        grid.bind(minimum_height=grid.setter('height'))

        btn_easy = MenuButton(text="FÁCIL", size_hint=(1, None), height=56)
        btn_normal = MenuButton(text="NORMAL", size_hint=(1, None), height=56)
        btn_hard = MenuButton(text="DIFÍCIL", size_hint=(1, None), height=56)
        grid.add_widget(btn_easy)
        grid.add_widget(btn_normal)
        grid.add_widget(btn_hard)
        content.add_widget(grid)

        btn_cancel = ExitButton(text="CANCELAR", size_hint=(1, None), height=52)
        content.add_widget(btn_cancel)

        popup = Popup(title="Nivel 2 - Dificultad", content=content,
                      size_hint=(None, None), size=(410, 350), auto_dismiss=True)
        popup.separator_color = (0, 0, 0, 0)
        btn_easy.bind(on_press=lambda *_: (popup.dismiss(), self.start_level2("easy")))
        btn_normal.bind(on_press=lambda *_: (popup.dismiss(), self.start_level2("normal")))
        btn_hard.bind(on_press=lambda *_: (popup.dismiss(), self.start_level2("hard")))
        btn_cancel.bind(on_press=lambda *_: popup.dismiss())
        popup.open()

    def start_level2(self, difficulty: str):
        if self.app and hasattr(self.app, "start_level2"):
            self.app.start_level2(difficulty)

class LevelScreen(Widget):
    """Pantalla de selección de niveles"""
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        # Fondo
        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo1.png",
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
            Color(0, 0, 0, 0.65)
            self.overlay = Rectangle(
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
        
        # Título
        self.title = Label(
            text="[b]SELECCIONA NIVEL[/b]",
            markup=True,
            font_size='48sp',
            color=(1, 0.9, 0.2, 1),
            size_hint=(None, None),
            size=(Window.width, 80),
            pos=(0, Window.height - 150)
        )
        self.add_widget(self.title)
        
        # Botón Nivel 1
        self.level1_button = MenuButton(text="NIVEL 1")
        self.level1_button.pos = (Window.width / 2 - 160, Window.height / 2)
        self.level1_button.bind(on_press=self.start_level1)
        self.add_widget(self.level1_button)
        
        # Botón Volver
        self.back_button = ExitButton(text="VOLVER")
        self.back_button.pos = (Window.width / 2 - 160, 120)
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)
    
    def start_level1(self, instance):
        """Inicia el nivel 1"""
        print("Iniciando Nivel 1...")
        self.app.start_level1()
    
    def go_back(self, instance):
        """Vuelve al menú principal"""
        self.app.show_main_menu()


class InstructionsScreen(Widget):
    """Pantalla de instrucciones"""
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        # Fondo
        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo1.png",
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
            Color(0, 0, 0, 0.75)
            self.overlay = Rectangle(
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
        
        # Título
        self.title = Label(
            text="[b]INSTRUCCIONES[/b]",
            markup=True,
            font_size='48sp',
            color=(1, 0.9, 0.2, 1),
            size_hint=(None, None),
            size=(Window.width, 80),
            pos=(0, Window.height - 150)
        )
        self.add_widget(self.title)
        
        # Texto de instrucciones mejorado
        instructions_text = """
[b][size=26]COMO JUGAR:[/size][/b]

Toca o arrastra en la pantalla para mover tu ave

Evita colisionar con los enemigos

Esquiva los proyectiles enemigos

Algunos enemigos te siguen

Sobrevive el mayor tiempo posible

[b][color=20ff20]Buena suerte, piloto![/color][/b]
"""
        
        self.instructions_label = Label(
            text=instructions_text,
            markup=True,
            font_size='24sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(Window.width - 100, Window.height - 300),
            pos=(50, 150),
            halign="left",
            valign="top"
        )
        self.instructions_label.text_size = (Window.width - 100, None)
        self.add_widget(self.instructions_label)
        
        # Botón Volver
        self.back_button = ExitButton(text="VOLVER")
        self.back_button.pos = (Window.width / 2 - 160, 120)
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)
    
    def go_back(self, instance):
        """Vuelve al menú principal"""
        self.app.show_main_menu()
