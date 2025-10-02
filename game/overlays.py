from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.app import App
import random


class OverlayButton(Button):
    """Botón estilizado para overlays con animación de rebote y dibujo gráfico."""
    def __init__(self, button_type="normal", **kwargs):
        super().__init__(**kwargs)
        self.button_type = button_type
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.font_size = '24sp'
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.base_size = kwargs.get('size', (320, 70))
        self.size = self.base_size
        
        colors = {
            "normal": ((0.15, 0.5, 0.85, 0.95), (0.3, 0.7, 1, 0.8)),
            "success": ((0.2, 0.7, 0.3, 0.95), (0.3, 1, 0.4, 0.8)),
            "danger": ((0.7, 0.2, 0.2, 0.95), (1, 0.3, 0.3, 0.8)),
            "warning": ((0.8, 0.6, 0.1, 0.95), (1, 0.8, 0.2, 0.8))
        }
        
        bg_color, border_color = colors.get(button_type, colors["normal"])
        self.bg_color_normal = bg_color
        self.bg_color_pressed = (bg_color[0]*0.7, bg_color[1]*0.7, bg_color[2]*0.7, 1)
        
        with self.canvas.before:
            Color(0, 0, 0, 0.4)
            self.shadow = RoundedRectangle(
                pos=(self.pos[0] + 4, self.pos[1] - 4),
                size=self.size,
                radius=[15]
            )
            self.bg_color = Color(*self.bg_color_normal)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15]
            )
            self.border_draw_color = Color(*border_color)
            self.border_rect = Line(
                rounded_rectangle=(self.pos[0], self.pos[1], 
                                    self.size[0], self.size[1], 15),
                width=2.5
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
    
    def update_rect(self, *args):
        self.shadow.pos = (self.pos[0] + 4, self.pos[1] - 4)
        self.shadow.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.rounded_rectangle = (self.pos[0], self.pos[1], 
                                              self.size[0], self.size[1], 15)
    
    def on_button_press(self, instance):
        self.bg_color.rgba = self.bg_color_pressed
        anim = Animation(size=(self.base_size[0] - 10, self.base_size[1] - 5), duration=0.06)
        anim.start(self)
    
    def on_button_release(self, instance):
        self.bg_color.rgba = self.bg_color_normal
        anim = Animation(size=self.base_size, duration=0.1)
        anim.start(self)


class PauseMenu(Widget):
    """Menú de pausa mejorado con dimensiones ajustadas."""
    def __init__(self, game_screen, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        
        self.panel_width = 380
        self.panel_height = 430
        self.panel_x = Window.width / 2 - self.panel_width / 2
        self.panel_y = Window.height / 2 - self.panel_height / 2
        self.button_width = 300
        self.button_spacing = 85

        with self.canvas.before:
            Color(0, 0, 0.05, 0.88)
            self.overlay = Rectangle(
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
        
        with self.canvas:
            Color(0, 0, 0, 0.5)
            RoundedRectangle(
                pos=(self.panel_x + 6, self.panel_y - 6),
                size=(self.panel_width, self.panel_height),
                radius=[30]
            )
            Color(0.08, 0.12, 0.18, 0.98)
            self.panel = RoundedRectangle(
                pos=(self.panel_x, self.panel_y),
                size=(self.panel_width, self.panel_height),
                radius=[30]
            )
            Color(0.3, 0.6, 1, 0.6)
            Line(
                rounded_rectangle=(self.panel_x + 10, self.panel_y + self.panel_height - 100,
                                    self.panel_width - 20, 2, 1),
                width=2
            )
            Color(0.2, 0.5, 0.9, 0.7)
            Line(
                rounded_rectangle=(self.panel_x, self.panel_y, self.panel_width, self.panel_height, 30),
                width=3
            )
        
        self.title = Label(
            text="[b]PAUSA[/b]",
            markup=True,
            font_size='52sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(self.panel_width, 60),
            pos=(self.panel_x, self.panel_y + self.panel_height - 80)
        )
        self.add_widget(self.title)
        
        self.subtitle = Label(
            text="Vuelo detenido, respira...",
            font_size='18sp',
            color=(0.7, 0.8, 1, 0.8),
            italic=True,
            size_hint=(None, None),
            size=(self.panel_width, 30),
            pos=(self.panel_x, self.panel_y + self.panel_height - 130)
        )
        self.add_widget(self.subtitle)
        
        # Centramos dentro del panel
        button_x = self.panel_x + (self.panel_width - self.button_width) / 2
        button_y = self.panel_y + self.panel_height - 220
        
        self.resume_button = OverlayButton(
            text="REANUDAR", 
            button_type="success", 
            size=(self.button_width, 70)
        )
        self.resume_button.pos = (button_x, button_y)
        self.resume_button.font_size = '26sp'
        self.resume_button.bind(on_press=self.resume_game)
        self.add_widget(self.resume_button)
        
        self.retry_button = OverlayButton(
            text="REINTENTAR", 
            button_type="warning", 
            size=(self.button_width, 70)
        )
        self.retry_button.pos = (button_x, button_y - self.button_spacing)
        self.retry_button.bind(on_press=self.retry_game)
        self.add_widget(self.retry_button)
        
        self.menu_button = OverlayButton(
            text="MENÚ PRINCIPAL", 
            button_type="danger",
            size=(self.button_width, 70)
        )
        self.menu_button.pos = (button_x, button_y - self.button_spacing * 2)
        self.menu_button.bind(on_press=self.go_to_menu)
        self.add_widget(self.menu_button)
    
    def resume_game(self, instance):
        self.game_screen.toggle_pause()
    
    def retry_game(self, instance):
        self.game_screen.restart_game()
    
    def go_to_menu(self, instance):
        self.game_screen.go_to_main_menu()


class GameOverMenu(Widget):
    """Menú de Game Over mejorado con dimensiones ajustadas."""
    def __init__(self, game_screen, final_score, **kwargs):
        super().__init__(**kwargs)
        self.game_screen = game_screen
        self.final_score = final_score

        self.panel_width = 400
        self.panel_height = 500
        self.panel_x = Window.width / 2 - self.panel_width / 2
        self.panel_y = Window.height / 2 - self.panel_height / 2
        self.button_width = 300
        self.button_spacing = 85
        
        with self.canvas.before:
            Color(0.1, 0, 0, 0.9)
            self.overlay = Rectangle(
                size=(Window.width, Window.height),
                pos=(0, 0)
            )
        
        with self.canvas:
            Color(0, 0, 0, 0.6)
            RoundedRectangle(
                pos=(self.panel_x + 8, self.panel_y - 8),
                size=(self.panel_width, self.panel_height),
                radius=[35]
            )
            Color(0.12, 0.05, 0.08, 0.98)
            self.panel = RoundedRectangle(
                pos=(self.panel_x, self.panel_y),
                size=(self.panel_width, self.panel_height),
                radius=[35]
            )
            Color(1, 0.2, 0.3, 0.8)
            Line(
                rounded_rectangle=(self.panel_x, self.panel_y, self.panel_width, self.panel_height, 35),
                width=3.5
            )
        
        self.title = Label(
            text="[b]GAME OVER[/b]",
            markup=True,
            font_size='58sp',
            color=(1, 0.95, 0.95, 1),
            size_hint=(None, None),
            size=(self.panel_width, 70),
            pos=(self.panel_x, self.panel_y + self.panel_height - 80)
        )
        self.add_widget(self.title)
        
        defeat_messages = [
            "El cielo te venció", "Caíste en batalla", "La tormenta fue implacable",
            "Los enemigos ganaron esta vez", "El vuelo llegó a su fin"
        ]
        self.defeat_label = Label(
            text=random.choice(defeat_messages),
            font_size='19sp',
            color=(1, 0.6, 0.6, 0.9),
            italic=True,
            size_hint=(None, None),
            size=(self.panel_width, 30),
            pos=(self.panel_x, self.panel_y + self.panel_height - 130)
        )
        self.add_widget(self.defeat_label)
        
        self.score_label = Label(
            text="[b]PUNTUACIÓN FINAL[/b]",
            markup=True,
            font_size='24sp',
            color=(1, 0.9, 0.4, 1),
            size_hint=(None, None),
            size=(self.panel_width, 40),
            pos=(self.panel_x, self.panel_y + self.panel_height - 200)
        )
        self.add_widget(self.score_label)
        
        self.score_value = Label(
            text=f"[b]{final_score}[/b]",
            markup=True,
            font_size='68sp',
            color=(0.3, 1, 0.5, 1),
            size_hint=(None, None),
            size=(self.panel_width, 80),
            pos=(self.panel_x, self.panel_y + self.panel_height - 280)
        )
        self.add_widget(self.score_value)
        
        messages = [
            "No te rindas, guerrero", "Cada intento te hace mejor", 
            "El cóndor volará más alto", "La práctica hace al maestro",
            "Casi alcanzas la gloria"
        ]
        self.message_label = Label(
            text=random.choice(messages),
            markup=True,
            font_size='20sp',
            color=(0.9, 0.9, 1, 0.95),
            bold=True,
            size_hint=(None, None),
            size=(self.panel_width, 40),
            pos=(self.panel_x, self.panel_y + self.panel_height - 350)
        )
        self.add_widget(self.message_label)

        button_x = self.panel_x + (self.panel_width - self.button_width) / 2
        button_y = self.panel_y + 130
        
        self.retry_button = OverlayButton(
            text="REINTENTAR", 
            button_type="success", 
            size=(self.button_width, 70)
        )
        self.retry_button.pos = (button_x, button_y)
        self.retry_button.font_size = '28sp'
        self.retry_button.bind(on_press=self.retry_game)
        self.add_widget(self.retry_button)
        
        self.menu_button = OverlayButton(
            text="MENÚ PRINCIPAL", 
            button_type="danger",
            size=(self.button_width, 70)
        )
        self.menu_button.pos = (button_x, button_y - self.button_spacing)
        self.menu_button.bind(on_press=self.go_to_menu)
        self.add_widget(self.menu_button)
        
    def retry_game(self, instance):
        self.game_screen.restart_game()
    
    def go_to_menu(self, instance):
        self.game_screen.go_to_main_menu()


class PauseButton(Button):
    """Botón de pausa flotante mejorado"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.text = "II"
        self.font_size = '28sp'
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.base_size = (70, 70)
        self.size = self.base_size
        self.pos = (Window.width - 90, Window.height - 90)
        
        with self.canvas.before:
            Color(0, 0, 0, 0.5)
            self.shadow = RoundedRectangle(
                pos=(self.pos[0] + 3, self.pos[1] - 3),
                size=self.size,
                radius=[self.base_size[0] / 2]
            )
            Color(0.15, 0.2, 0.35, 0.92)
            self.bg_circle = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.base_size[0] / 2]
            )
            Color(0.4, 0.65, 1, 0.8)
            self.border_circle = Line(
                circle=(self.center_x, self.center_y, self.base_size[0] / 2 - 1),
                width=3
            )
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)
        
        breathe = (Animation(size=(75, 75), duration=1.5, t='in_out_sine') + 
                   Animation(size=(70, 70), duration=1.5, t='in_out_sine'))
        breathe.repeat = True
        breathe.start(self)
    
    def update_graphics(self, *args):
        radius = self.size[0] / 2
        self.shadow.pos = (self.pos[0] + 3, self.pos[1] - 3)
        self.shadow.size = self.size
        self.shadow.radius = [radius]
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size
        self.bg_circle.radius = [radius]
        self.border_circle.circle = (self.center_x, self.center_y, radius - 1.5)
    
    def on_button_press(self, instance):
        anim = Animation(size=(65, 65), duration=0.08)
        anim.start(self)
    
    def on_button_release(self, instance):
        anim = Animation(size=self.base_size, duration=0.12)
        anim.start(self)


class GameScreen(Widget):
    """Placeholder para la pantalla de juego."""
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.is_paused = False
        self.final_score = 12345
        
        with self.canvas.before:
            Color(0.1, 0.1, 0.2, 1)
            Rectangle(size=(Window.width, Window.height))

        self.add_widget(Label(text="Juego Corriendo", font_size='32sp',
                              pos=(Window.width / 2 - 150, Window.height / 2)))

        self.pause_btn = PauseButton()
        self.pause_btn.bind(on_press=lambda *args: self.toggle_pause())
        self.add_widget(self.pause_btn)

        Clock.schedule_once(lambda dt: self.show_game_over(), 5)

    def toggle_pause(self):
        if not self.is_paused:
            self.pause_menu = PauseMenu(self)
            self.add_widget(self.pause_menu)
            self.is_paused = True
            print("Juego Pausado")
        else:
            self.remove_widget(self.pause_menu)
            self.is_paused = False
            print("Juego Reanudado")

    def show_game_over(self):
        self.remove_widget(self.pause_btn)
        self.game_over_menu = GameOverMenu(self, self.final_score)
        self.add_widget(self.game_over_menu)
        print("Game Over Mostrado")

    def restart_game(self):
        self.app.restart_game()
    
    def go_to_main_menu(self):
        self.app.show_main_menu()


class GameApp(App):
    def build(self):
        Window.size = (800, 600)
        self.root_widget = Widget()
        self.game_screen = GameScreen(self)
        self.root_widget.add_widget(self.game_screen)
        return self.root_widget

    def show_main_menu(self):
        print("Volviendo al menú principal...")
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(Label(text="Pantalla de Menú Principal"))
    
    def restart_game(self):
        print("Reiniciando juego...")
        self.root_widget.clear_widgets()
        self.game_screen = GameScreen(self)
        self.root_widget.add_widget(self.game_screen)


if __name__ == '__main__':
    GameApp().run()
