# main.py
from kivy.config import Config

Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '960')

from kivy.app import App
from kivy.uix.widget import Widget
from game.screen import GameScreen
from game.menu import MainMenu, LevelScreen, InstructionsScreen
from kivy.core.audio import SoundLoader

# --- NUEVA IMPORTACIÓN ---
from game.trajectory_screen import TrajectoryGameScreen
# -------------------------

class RootWidget(Widget):
    """Widget raíz que contiene todas las pantallas"""
    pass


class MyGameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_widget = None
        self.music = SoundLoader.load('images/musica.mp3')
        if self.music:
            self.music.loop = True 
            self.music.volume = 0.5 
            
    def build(self):
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
    
    def start_game(self):
        """Inicia el juego (MODO NAVE)"""
        self.root_widget.clear_widgets()
        game = GameScreen()
        self.root_widget.add_widget(game)
        
    # --- MÉTODO NUEVO ---
    def start_trajectory_game(self):
        """Inicia el juego (MODO TRAYECTORIA)"""
        self.root_widget.clear_widgets()
        game = TrajectoryGameScreen()
        self.root_widget.add_widget(game)
    # --------------------


if __name__ == "__main__":
    MyGameApp().run()