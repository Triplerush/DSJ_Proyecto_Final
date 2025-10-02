import math

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def normalize_vector(vx, vy):
    """Normaliza un vector a longitud 1"""
    length = math.sqrt(vx**2 + vy**2)
    if length > 0:
        return vx / length, vy / length
    return 0, 0

def limit_vector(vx, vy, max_length):
    """Limita la magnitud de un vector"""
    length = math.sqrt(vx**2 + vy**2)
    if length > max_length:
        return (vx / length) * max_length, (vy / length) * max_length
    return vx, vy

def calculate_separation(enemy, enemies, separation_radius=100):
    """Regla 1: Separación - Evita chocar con vecinos cercanos"""
    steer_x = 0
    steer_y = 0
    count = 0
    
    for other in enemies:
        if other != enemy and other.use_flocking:
            dist = distance(enemy.center_x, enemy.center_y, other.center_x, other.center_y)
            if 0 < dist < separation_radius:
                # Vector alejándose del vecino
                diff_x = enemy.center_x - other.center_x
                diff_y = enemy.center_y - other.center_y
                # Peso inversamente proporcional al cuadrado de la distancia
                diff_x /= (dist * dist)
                diff_y /= (dist * dist)
                steer_x += diff_x
                steer_y += diff_y
                count += 1
    
    if count > 0:
        steer_x /= count
        steer_y /= count
    
    return steer_x, steer_y

def calculate_alignment(enemy, enemies, alignment_radius=150):
    """Regla 2: Alineación - Dirígete en la dirección promedio de los vecinos"""
    avg_vx = 0
    avg_vy = 0
    count = 0
    
    for other in enemies:
        if other != enemy and other.use_flocking:
            dist = distance(enemy.center_x, enemy.center_y, other.center_x, other.center_y)
            if 0 < dist < alignment_radius:
                avg_vx += other.velocity_x
                avg_vy += other.velocity_y
                count += 1
    
    if count > 0:
        avg_vx /= count
        avg_vy /= count
        # Calcular fuerza de dirección
        steer_x = avg_vx - enemy.velocity_x
        steer_y = avg_vy - enemy.velocity_y
        return steer_x, steer_y
    
    return 0, 0

def calculate_cohesion(enemy, enemies, cohesion_radius=200):
    """Regla 3: Cohesión - Muévete hacia el centro de masa de los vecinos"""
    center_x = 0
    center_y = 0
    count = 0
    
    for other in enemies:
        if other != enemy and other.use_flocking:
            dist = distance(enemy.center_x, enemy.center_y, other.center_x, other.center_y)
            if 0 < dist < cohesion_radius:
                center_x += other.center_x
                center_y += other.center_y
                count += 1
    
    if count > 0:
        center_x /= count
        center_y /= count
        # Vector hacia el centro
        steer_x = center_x - enemy.center_x
        steer_y = center_y - enemy.center_y
        steer_x, steer_y = normalize_vector(steer_x, steer_y)
        return steer_x, steer_y
    
    return 0, 0

def apply_flocking(enemy, enemies, separation_weight=3.0, alignment_weight=1.2, cohesion_weight=0.8):
    """Aplica las tres reglas de flocking con pesos personalizables"""
    # Calcular las tres fuerzas
    sep_x, sep_y = calculate_separation(enemy, enemies)
    align_x, align_y = calculate_alignment(enemy, enemies)
    coh_x, coh_y = calculate_cohesion(enemy, enemies)
    
    # Aplicar pesos
    sep_x *= separation_weight
    sep_y *= separation_weight
    align_x *= alignment_weight
    align_y *= alignment_weight
    coh_x *= cohesion_weight
    coh_y *= cohesion_weight
    
    # Sumar todas las fuerzas
    total_x = sep_x + align_x + coh_x
    total_y = sep_y + align_y + coh_y
    
    return total_x, total_y
