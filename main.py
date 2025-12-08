from kivy.config import Config

# Configuración gráfica inicial
Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '960')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.utils import platform  # <--- IMPORTANTE: Necesario para detectar Android

# Importaciones de tus pantallas y lógica de juego
from game.screen import GameScreen
from game.menu import MainMenu, LevelScreen, InstructionsScreen
from game.trajectory_screen import TrajectoryGameScreen
from game.level3_ar import ARGameScreen

class RootWidget(Widget):
    """Widget raíz que contiene todas las pantallas"""
    pass

class MyGameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_widget = None
        
        # Carga de música (con manejo de errores por si no existe el archivo)
        self.music = SoundLoader.load('images/musica.mp3')
        if self.music:
            self.music.loop = True 
            self.music.volume = 0.5 
            
    def build(self):
        # --- BLOQUE NUEVO PARA PERMISOS ANDROID ---
        # Esto evita que la app se cierre al intentar abrir la cámara en el Nivel 3
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            
            def callback(permission, results):
                if all([res for res in results]):
                    print("Permisos de cámara concedidos.")
                else:
                    print("Permisos de cámara denegados.")
            
            # Solicitamos permiso explícito al usuario al arrancar la app
            request_permissions([Permission.CAMERA], callback)
        # ------------------------------------------

        self.root_widget = RootWidget()
        
        if self.music:
            self.music.play()
    
        self.show_main_menu()
        return self.root_widget
    
    def show_main_menu(self):
        """Muestra el menú principal"""
        self.root_widget.clear_widgets()
        menu = MainMenu(app_instance=self)
        self.root_widget.add_widget(menu)
    
    def show_level_screen(self):
        """Muestra la pantalla de selección de niveles"""
        self.root_widget.clear_widgets()
        level_screen = LevelScreen(app_instance=self)
        self.root_widget.add_widget(level_screen)
    
    def show_instructions_screen(self):
        """Muestra la pantalla de instrucciones"""
        self.root_widget.clear_widgets()
        instructions = InstructionsScreen(app_instance=self)
        self.root_widget.add_widget(instructions)
    
    def _set_screen(self, widget: Widget):
        """Helper para cambiar el widget actual en pantalla"""
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(widget)

    # Nivel 1 (modo nave)
    def start_level1(self):
        game = GameScreen()
        self._set_screen(game)

    def start_game(self):
        """Inicia el juego (Redirecciona a Nivel 1 por defecto)"""
        self.start_level1()
        
    # Nivel 2 (trayectoria) con selección de dificultad
    def start_level2(self, difficulty: str = "normal"):
        if TrajectoryGameScreen is None:
            print("Nivel 2 no disponible: trajectory_screen.py no importable.")
            return
            
        # Intentar pasar dificultad al constructor
        try:
            game = TrajectoryGameScreen(difficulty=difficulty)
        except TypeError:
            # Fallback si la clase no aceptara argumentos (por seguridad)
            game = TrajectoryGameScreen()
            if hasattr(game, "set_difficulty"):
                game.set_difficulty(difficulty)
                
        self._set_screen(game)
        
    # Nivel 3 (Modo AR)
    def start_level3(self):
        """Inicia el Nivel 3 (Modo AR con Cámara)"""
        try:
            game = ARGameScreen()
            self._set_screen(game)
        except Exception as e:
            print(f"Error iniciando Nivel 3: {e}")
            # Si falla la cámara, regresamos al Nivel 2 difícil como respaldo
            self.start_level2("hard")

if __name__ == "__main__":
    MyGameApp().run()
