# game/trajectory.py
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window

# ¡Debe ser el mismo valor que en physics_projectile.py!
GRAVITY_FORCE = -150.0

class Trajectory(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configuración de los puntos (como en Unity)
        self.dots_number = 30
        self.dot_spacing = 0.2  # Tiempo (en segundos) entre cada punto
        self.dot_size = (8, 8)
        
        self.dots_list = []
        self.prepare_dots()
        self.hide() # Ocultar al inicio

    def prepare_dots(self):
        """Crea los puntos y los añade al canvas."""
        for i in range(self.dots_number):
            # Usamos el canvas de este widget para dibujar
            with self.canvas:
                # Damos un color (blanco semitransparente)
                Color(1, 1, 1, 0.8)
                # Creamos el punto (Ellipse)
                dot = Ellipse(pos=(0, 0), size=self.dot_size)
            
            self.dots_list.append(dot)

    def update_dots(self, start_pos, force_applied):
        """
        Calcula y actualiza la posición de todos los puntos
        basado en la fórmula de tiro parabólico.
        """
        
        # Este 'timeStamp' es el 't' en la fórmula
        time_stamp = self.dot_spacing 
        
        # Iteramos sobre cada punto y calculamos su posición futura
        for dot in self.dots_list:
            
            # --- FÓRMULA DE TIRO PARABÓLICO (de Unity) ---
            # p = p0 + v0*t + 0.5*g*t^2
            
            # Posición X = pos_inicial_x + velocidad_x * tiempo
            pos_x = start_pos[0] + force_applied[0] * time_stamp
            
            # Posición Y = pos_inicial_y + velocidad_y * tiempo + 0.5 * gravedad * tiempo^2
            pos_y = start_pos[1] + force_applied[1] * time_stamp + \
                    (0.5 * GRAVITY_FORCE * (time_stamp ** 2))
            
            # Actualizamos la posición del punto en el canvas
            dot.pos = (pos_x - self.dot_size[0] / 2, pos_y - self.dot_size[1] / 2)
            
            # Incrementamos el tiempo para el siguiente punto
            time_stamp += self.dot_spacing

    def show(self):
        """Muestra la trayectoria."""
        self.canvas.opacity = 1.0
        
    def hide(self):
        """Oculta la trayectoria."""
        self.canvas.opacity = 0.0