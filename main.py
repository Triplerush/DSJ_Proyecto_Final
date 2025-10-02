from kivy.config import Config

Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '960')

from kivy.app import App
from kivy.uix.widget import Widget
from game.screen import GameScreen
from game.menu import MainMenu, LevelScreen, InstructionsScreen


class RootWidget(Widget):
    """Widget raíz que contiene todas las pantallas"""
    pass


class MyGameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_widget = None
    
    def build(self):
        # Crear el widget raíz
        self.root_widget = RootWidget()
        # Mostrar el menú principal al iniciar
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
        """Inicia el juego"""
        self.root_widget.clear_widgets()
        game = GameScreen()
        self.root_widget.add_widget(game)


if __name__ == "__main__":
    MyGameApp().run()
