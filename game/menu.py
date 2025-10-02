from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
import random


class MenuButton(Button):
    """Botón personalizado para el menú"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 0.9, 0.8)
        self.background_normal = ''
        self.font_size = '28sp'
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.size = (300, 70)
        
        # Animación de hover
        self.bind(on_press=self.on_button_press)
    
    def on_button_press(self, instance):
        """Animación al presionar el botón"""
        anim = Animation(size=(320, 75), duration=0.1) + Animation(size=(300, 70), duration=0.1)
        anim.start(self)


class MainMenu(Widget):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        # Fondo del menú
        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo1.png",
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
            # Overlay oscuro para mejor legibilidad
            Color(0, 0, 0, 0.5)
            self.overlay = Rectangle(
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
        
        # Título del juego
        self.title = Label(
            text="[b]EL VUELO DEL CÓNDOR[/b]",
            markup=True,
            font_size='72sp',
            color=(1, 0.9, 0.2, 1),
            size_hint=(None, None),
            size=(Window.width, 100),
            pos=(0, Window.height - 180)
        )
        self.add_widget(self.title)
        
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
                size=(100, 100),
                pos=(50 + i * (Window.width - 150), Window.height - 300)
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
                size=(80, 80),
                pos=(100 + i * 150, 100)
            )
            self.add_widget(sprite)
            self.enemy_sprites.append(sprite)
        
        # Iniciar animaciones de sprites
        Clock.schedule_interval(self.animate_sprites, 0.15)
        
        # Botones del menú
        button_y = Window.height / 2 + 50
        button_spacing = 90
        
        # Botón Jugar
        self.play_button = MenuButton(text="JUGAR")
        self.play_button.pos = (Window.width / 2 - 150, button_y)
        self.play_button.bind(on_press=self.start_game)
        self.add_widget(self.play_button)
        
        # Botón Nivel
        self.level_button = MenuButton(text="NIVEL")
        self.level_button.pos = (Window.width / 2 - 150, button_y - button_spacing)
        self.level_button.bind(on_press=self.show_levels)
        self.add_widget(self.level_button)
        
        # Botón Instrucciones
        self.instructions_button = MenuButton(text="INSTRUCCIONES")
        self.instructions_button.pos = (Window.width / 2 - 150, button_y - button_spacing * 2)
        self.instructions_button.bind(on_press=self.show_instructions)
        self.add_widget(self.instructions_button)
        
        # Botón Opciones
        self.options_button = MenuButton(text="OPCIONES")
        self.options_button.pos = (Window.width / 2 - 150, button_y - button_spacing * 3)
        self.options_button.bind(on_press=self.show_options)
        self.add_widget(self.options_button)
        
        # Versión del juego
        self.version_label = Label(
            text="v1.0",
            font_size='14sp',
            color=(1, 1, 1, 0.6),
            size_hint=(None, None),
            size=(100, 30),
            pos=(Window.width - 110, 10)
        )
        self.add_widget(self.version_label)
    
    def animate_title(self):
        """Animación pulsante del título"""
        anim = (Animation(font_size=76, duration=1) + 
                Animation(font_size=72, duration=1))
        anim.repeat = True
        anim.start(self.title)
    
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
            Color(0, 0, 0, 0.6)
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
        self.level1_button.pos = (Window.width / 2 - 150, Window.height / 2)
        self.level1_button.bind(on_press=self.start_level1)
        self.add_widget(self.level1_button)
        
        # Botón Volver
        self.back_button = MenuButton(text="VOLVER")
        self.back_button.pos = (Window.width / 2 - 150, 100)
        self.back_button.background_color = (0.6, 0.2, 0.2, 0.8)
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)
    
    def start_level1(self, instance):
        """Inicia el nivel 1"""
        print("Iniciando Nivel 1...")
        self.app.start_game()
    
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
            Color(0, 0, 0, 0.7)
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
        
        # Texto de instrucciones
        instructions_text = """
[b]CÓMO JUGAR:[/b]

• Toca o arrastra en la pantalla para mover tu ave

• Evita colisionar con los enemigos

• Esquiva los proyectiles enemigos

• Algunos enemigos te siguen

• Sobrevive el mayor tiempo posible

[b]¡Buena suerte, piloto![/b]
        """
        
        self.instructions_label = Label(
            text=instructions_text,
            markup=True,
            font_size='22sp',
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
        self.back_button = MenuButton(text="VOLVER")
        self.back_button.pos = (Window.width / 2 - 150, 50)
        self.back_button.background_color = (0.6, 0.2, 0.2, 0.8)
        self.back_button.bind(on_press=self.go_back)
        self.add_widget(self.back_button)
    
    def go_back(self, instance):
        """Vuelve al menú principal"""
        self.app.show_main_menu()
