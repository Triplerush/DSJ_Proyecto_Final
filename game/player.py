from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock


class Player(Widget):
    target_x = NumericProperty(0)
    target_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite = Image(source="assets/images/player.png", size_hint=(None, None))
        self.sprite.size = (80, 80)
        self.add_widget(self.sprite)

        self.center_x = Window.width / 2
        self.y = 50
        self.target_x = self.center_x
        self.target_y = self.center_y
        self.update_sprite()

        Clock.schedule_interval(self.update, 1 / 60)

    def update_sprite(self):
        self.sprite.center_x = self.center_x
        self.sprite.center_y = self.center_y

    def update(self, dt):
        speed = 15
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y

        if abs(dx) > speed:
            self.center_x += speed if dx > 0 else -speed
        else:
            self.center_x = self.target_x

        if abs(dy) > speed:
            self.center_y += speed if dy > 0 else -speed
        else:
            self.center_y = self.target_y

        self.update_sprite()

    def move_to(self, touch):
        self.target_x = touch.x
        self.target_y = touch.y
