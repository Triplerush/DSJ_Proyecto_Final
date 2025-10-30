# game/geometry.py
from typing import Tuple

Vec2 = Tuple[float, float]
Rect = Tuple[float, float, float, float]  # x, y, w, h

def rects_intersect(a: Rect, b: Rect) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)

def point_in_rect(p: Vec2, r: Rect) -> bool:
    x, y = p
    rx, ry, rw, rh = r
    return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)

def segments_intersect(p1: Vec2, p2: Vec2, p3: Vec2, p4: Vec2) -> bool:
    def ccw(A, B, C):
        return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
    return (ccw(p1,p3,p4) != ccw(p2,p3,p4)) and (ccw(p1,p2,p3) != ccw(p1,p2,p4))

def segment_intersects_rect(p1: Vec2, p2: Vec2, r: Rect) -> bool:
    # rápido: si un punto está adentro
    if point_in_rect(p1, r) or point_in_rect(p2, r):
        return True
    x, y, w, h = r
    edges = [
        ((x, y), (x+w, y)),
        ((x+w, y), (x+w, y+h)),
        ((x+w, y+h), (x, y+h)),
        ((x, y+h), (x, y))
    ]
    for a, b in edges:
        if segments_intersect(p1, p2, a, b):
            return True
    return False

def expand_rect(r: Rect, pad: float) -> Rect:
    x, y, w, h = r
    return (x - pad, y - pad, w + 2*pad, h + 2*pad)