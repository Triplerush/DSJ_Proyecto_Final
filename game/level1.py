# game/level1.py
from typing import List, Tuple
from dataclasses import dataclass
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty
from .geometry import Rect


@dataclass
class WallSpec:
    x: float
    y: float
    w: float
    h: float

    @property
    def rect(self) -> Rect:
        return (self.x, self.y, self.w, self.h)


class Wall(Widget):
    # más opacas: alpha = 0.8
    color = ListProperty([0.95, 0.55, 0.25, 0.8])

    def __init__(self, spec: WallSpec, **kwargs):
        super().__init__(**kwargs)
        self.x, self.y = spec.x, spec.y
        self.width, self.height = spec.w, spec.h
        with self.canvas:
            Color(*self.color)
            self._rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_):
        if self._rect is not None:
            self._rect.pos = self.pos
            self._rect.size = self.size


@dataclass
class Waypoint:
    id: str
    pos: Tuple[float, float]


class Level1Spec:
    """
    Distribución pensada para la pantalla alta que mostraste:
    - Jugador abajo-izq (~50,100) queda libre.
    - Obstáculos van subiendo en forma de escalera hacia la derecha.
    - 6 paredes en total.
    """

    def __init__(self):
       self.walls: List[WallSpec] = [
            WallSpec(0, 60, 460, 30),  

            WallSpec(420, 90, 40, 180),

            WallSpec(320, 340, 160, 30),


            WallSpec(260, 480, 40, 220),


            WallSpec(60, 580, 40, 180),
        ]
        
    def realize(self, parent: Widget):
        widgets = []
        for ws in self.walls:
            w = Wall(ws)
            parent.add_widget(w)
            widgets.append(w)
        wall_rects = [ws.rect for ws in self.walls]
        return widgets, wall_rects