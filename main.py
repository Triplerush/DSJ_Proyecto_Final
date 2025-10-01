from kivy.app import App
from game.screen import GameScreen

class MyGameApp(App):
    def build(self):
        return GameScreen()

if __name__ == "__main__":
    MyGameApp().run()
