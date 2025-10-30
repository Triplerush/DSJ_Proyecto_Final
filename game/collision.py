# game/collision.py
from typing import Tuple, List
from .geometry import rects_intersect, Rect

def move_with_collisions(x: float, y: float, w: float, h: float,
                         vx: float, vy: float, dt: float,
                         walls: List[Rect]) -> Tuple[float, float, float, float, bool]:
    """
    Desplaza en X y Y con corrección de penetración (1px) y devuelve si hubo colisión.
    Retorna: (nx, ny, nvx, nvy, collided)
    """
    collided = False

    # Eje X
    nx = x + vx * dt
    ny = y
    aabb = (nx, ny, w, h)
    if any(rects_intersect(aabb, wr) for wr in walls):
        step = -1 if vx > 0 else 1
        while any(rects_intersect((nx, ny, w, h), wr) for wr in walls):
            nx += step
        vx = 0.0
        collided = True

    # Eje Y
    ny = y + vy * dt
    aabb = (nx, ny, w, h)
    if any(rects_intersect(aabb, wr) for wr in walls):
        step = -1 if vy > 0 else 1
        while any(rects_intersect((nx, ny, w, h), wr) for wr in walls):
            ny += step
        vy = 0.0
        collided = True

    return nx, ny, vx, vy, collided