# game/collision.py
from typing import Tuple, List
from .geometry import rects_intersect, Rect

def move_with_collisions(x: float, y: float, w: float, h: float,
                         vx: float, vy: float, dt: float,
                         walls: List[Rect]) -> Tuple[float, float, float, float, bool]:
    """
    Desplaza en X y Y con corrección de penetración (1px) 
    y devuelve si hubo colisión.
    Retorna: (nx, ny, nvx, nvy, collided)
    """
    collided = False
    
    # --- EJE X ---
    nx = x + vx * dt
    ny = y
    aabb = (nx, ny, w, h)
    
    if any(rects_intersect(aabb, wr) for wr in walls):
        # Si vx es 0 (caída recta), forzamos step=0 para no moverlo infinitamente a la derecha
        if abs(vx) < 0.001: 
            step = 0 
        else:
            step = -1 if vx > 0 else 1
            
        # SAFETY: Límite de 50 iteraciones para evitar congelamiento
        safe_loop = 0 
        while safe_loop < 50 and any(rects_intersect((nx, ny, w, h), wr) for wr in walls):
            if step == 0: # Si no tiene velocidad horizontal, deshacemos el movimiento
                nx = x 
                break
            nx += step
            safe_loop += 1
            
        vx = 0.0
        collided = True

    # --- EJE Y ---
    # Usamos la nueva nx para calcular el movimiento en Y
    ny_target = y + vy * dt
    aabb = (nx, ny_target, w, h)
    
    if any(rects_intersect(aabb, wr) for wr in walls):
        step = -1 if vy > 0 else 1
        
        # Iniciar desde la posición tentativa
        current_ny = ny_target
        
        # SAFETY: Límite de 50 iteraciones
        safe_loop = 0
        while safe_loop < 50 and any(rects_intersect((nx, current_ny, w, h), wr) for wr in walls):
            current_ny += step
            safe_loop += 1
            
        ny = current_ny
        vy = 0.0
        collided = True
    else:
        ny = ny_target

    return nx, ny, vx, vy, collided