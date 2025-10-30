from typing import List, Tuple
from dataclasses import dataclass
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty
from .geometry import Rect

# =========================================================
# CLASES BASE DE PAREDES Y WAYPOINTS
# =========================================================

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


# =========================================================
# NIVEL 1 - PAREDES + WAYPOINTS
# =========================================================
class Level1Spec:
    """
    Nivel 1 con paredes y puntos de patrulla (waypoints)
    """

    def __init__(self):
        self.walls: List[WallSpec] = [
            WallSpec(0, 60, 460, 30),
            WallSpec(420, 90, 40, 180),
            WallSpec(320, 340, 160, 30),
            WallSpec(260, 480, 40, 220),
            WallSpec(60, 580, 40, 180),
        ]

        # Waypoints: ubicados sobre o cerca de las paredes
        self.waypoints: List[Waypoint] = [
            Waypoint("wp1", (120, 120)),
            Waypoint("wp2", (430, 180)),
            Waypoint("wp3", (380, 380)),
            Waypoint("wp4", (280, 520)),
            Waypoint("wp5", (80, 660)),
        ]

    def realize(self, parent: Widget):
        """Crea widgets de paredes y devuelve rectángulos y waypoints"""
        widgets = []
        for ws in self.walls:
            w = Wall(ws)
            parent.add_widget(w)
            widgets.append(w)
        wall_rects = [ws.rect for ws in self.walls]
        return widgets, wall_rects, self.waypoints
