# game/trajectory_screen.py
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.app import App

from game.slingshot_player import SlingshotPlayer
from game.physics_projectile import PhysicsProjectile
from game.trajectory import Trajectory

class TrajectoryGameScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. Fondo (fondo2.png)
        with self.canvas.before:
            self.bg = Rectangle(
                source="images/fondo2.png",
                size=Window.size,
                pos=(0, 0)
            )
            
        # 2. Crear al Jugador (Vicuña)
        self.player = SlingshotPlayer()
        # Posición fija de lanzamiento
        self.player.pos = (50, 100)
        self.launch_pos = self.player.center
        self.add_widget(self.player)
        
        # 3. Crear la Trayectoria
        self.trajectory = Trajectory()
        self.add_widget(self.trajectory)
        
        # 4. Lista para proyectiles (huevos)
        self.projectiles = []
        
        # 5. Variables de control (como en GameManager.cs)
        self.is_dragging = False
        self.start_point = None
        self.current_force = (0, 0)
        
        # --- MODIFICADO ---
        # 1. Esta variable ahora controla la POTENCIA MÁXIMA del lanzamiento
        # Sube este valor para que el proyectil vaya más rápido
        self.launch_power = 10.0  # (Antes se llamaba force_multiplier)
        
        # 2. --- NUEVA VARIABLE ---
        # Esta variable controla la SENSIBILIDAD (distancia máxima de arrastre en píxeles)
        # Un valor más bajo (ej. 100) te dará potencia máxima con menos arrastre.
        self.max_drag_distance = 150.0 
        # --------------------

        # Iniciar el bucle de juego (Update)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, dt):
        """Bucle principal del juego (60 FPS)."""
        
        # Actualizar todos los proyectiles en pantalla
        for projectile in self.projectiles[:]:
            is_alive = projectile.update(dt)
            
            if not is_alive:
                # Eliminar proyectil si salió de la pantalla
                self.projectiles.remove(projectile)
                self.remove_widget(projectile)

    def on_touch_down(self, touch):
        """Equivalente a OnDragStart() en Unity."""
        
        # Solo podemos empezar a arrastrar desde el jugador
        if self.player.collide_point(*touch.pos):
            self.is_dragging = True
            self.start_point = touch.pos
            
            # Cambiar sprite del jugador
            self.player.set_dragging(True)
            
            # Mostrar la trayectoria
            self.trajectory.show()
            
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        """Equivalente a OnDrag() en Unity."""
        if not self.is_dragging:
            return super().on_touch_move(touch)
            
        end_point = touch.pos
        
        # --- LÓGICA DE ARRASTRE TOTALMENTE MODIFICADA ---
        
        # 1. Calcular el vector de arrastre (inverso)
        dx = self.start_point[0] - end_point[0]
        dy = self.start_point[1] - end_point[1]
        
        # 2. Calcular la distancia (magnitud) del arrastre
        distance = (dx**2 + dy**2)**0.5
        
        # 3. Limitar (clamp) la distancia de arrastre
        
        # Si el arrastre es 0, evitamos división por cero
        if distance == 0:
            self.current_force = (0, 0)
            self.trajectory.update_dots(self.launch_pos, self.current_force)
            return True
            
        # Si la distancia de arrastre supera nuestro límite (max_drag_distance)...
        if distance > self.max_drag_distance:
            # Escalamos el vector (dx, dy) para que su longitud máxima sea max_drag_distance
            scale_factor = self.max_drag_distance / distance
            dx *= scale_factor
            dy *= scale_factor
            
            # Actualizamos la distancia para que sea el máximo
            distance = self.max_drag_distance
            
        # 4. Calcular la fuerza final
        # La potencia ahora es una proporción de la distancia de arrastre
        # (distance / max_drag_distance) nos da un valor entre 0.0 y 1.0
        # Lo multiplicamos por la potencia de lanzamiento (launch_power)
        # Y lo aplicamos al vector de dirección (normalizado)
        
        # Normalizar el vector de dirección
        norm_dx = dx / distance
        norm_dy = dy / distance
        
        # Calcular la potencia proporcional
        power_ratio = distance / self.max_drag_distance
        
        # La fuerza final es la dirección * potencia_proporcional * potencia_máxima
        # NOTA: En Kivy, el vector de fuerza ES la velocidad inicial.
        # Por eso multiplicamos por 100 para que tenga una buena velocidad base.
        # Ajusta este '100' si es necesario.
        force_x = norm_dx * power_ratio * (self.launch_power * 100)
        force_y = norm_dy * power_ratio * (self.launch_power * 100)
        
        # ----------------------------------------------------
        
        self.current_force = (force_x, force_y)
        
        # Actualizar la línea de trayectoria (la predicción)
        self.trajectory.update_dots(self.launch_pos, self.current_force)
        
        return True

    def on_touch_up(self, touch):
        """Equivalente a OnDragEnd() en Unity."""
        if not self.is_dragging:
            return super().on_touch_up(touch)
            
        self.is_dragging = False
        
        # 1. Cambiar sprite del jugador
        self.player.set_dragging(False)
        
        # 2. Ocultar trayectoria
        self.trajectory.hide()
        
        # 3. Lanzar el proyectil
        self.launch_projectile(self.current_force)
        
        self.current_force = (0, 0)
        return True

    def launch_projectile(self, force):
        """Crea y lanza el huevo."""
        
        # Creamos el proyectil en la posición de lanzamiento
        projectile = PhysicsProjectile(start_pos=self.launch_pos)
        
        # Le damos la fuerza/velocidad inicial
        projectile.push(force)
        
        # Lo añadimos a la pantalla y a la lista
        self.add_widget(projectile)
        self.projectiles.append(projectile)