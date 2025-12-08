from kivy.uix.widget import Widget
from kivy.uix.camera import Camera
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.graphics.context_instructions import PushMatrix, PopMatrix, Rotate
from kivy.utils import platform
from kivy.uix.label import Label
import random

# Importamos la lógica base
from game.trajectory_screen import TrajectoryGameScreen
from game.enemy_patrol import PatrolEnemy
from game.level1 import Waypoint

try:
    from plyer import accelerometer
except ImportError:
    accelerometer = None

class ARGameScreen(TrajectoryGameScreen):
    
    def __init__(self, **kwargs):
        # 1. Inicializamos la pantalla base (Nivel 2)
        super().__init__(difficulty="hard", **kwargs)
        
        # 2. BORRADO DE FONDO DEL NIVEL 2
        # Eliminamos la imagen de fondo para que no estorbe
        if hasattr(self, 'bg'):
            self.canvas.before.remove(self.bg)
            del self.bg

        # Agregamos un fondo NEGRO por seguridad (para que no se vea "fantasma")
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_black = Rectangle(size=Window.size, pos=(0,0))

        # 3. CONFIGURACIÓN DE CÁMARA ROBUSTA
        # Usamos resolución estándar
        self.camera = Camera(play=True, resolution=(640, 480))
        self.camera.allow_stretch = True
        self.camera.keep_ratio = False
        
        # --- TRUCO DE ROTACIÓN ---
        # 1. Le damos tamaño INVERTIDO: Ancho = Alto de Pantalla, Alto = Ancho de Pantalla.
        #    Esto crea un rectángulo "acostado" que cubre toda el área.
        self.camera.size_hint = (None, None)
        self.camera.size = (Window.height, Window.width)
        
        # 2. La centramos perfectamente en la pantalla
        self.camera.center = Window.center

        # 3. La rotamos -90 grados sobre SU PROPIO CENTRO.
        #    Al girar un rectángulo "acostado", se vuelve "parado" y llena la pantalla.
        with self.camera.canvas.before:
            PushMatrix()
            Rotate(angle=-90, origin=self.camera.center)
        with self.camera.canvas.after:
            PopMatrix()
        
        # Insertamos la cámara al fondo de la lista de widgets (index alto = dibujado al fondo)
        self.add_widget(self.camera, index=len(self.children)) 

        # 4. Variables de "Mundo Virtual" (Acelerómetro)
        self.camera_offset_x = 0.0
        self.world_width = 2000
        self.sensor_speed = 15.0

        # Activar sensores
        if platform == 'android':
            try:
                accelerometer.enable()
            except:
                print("Error iniciando acelerómetro")

        # Texto de ayuda
        self.info_label = Label(
            text="[b]Mueve tu celular a los lados\npara encontrar a los enemigos[/b]",
            markup=True, font_size='20sp',
            halign='center', pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        self.add_widget(self.info_label)

        # Crear enemigos
        self.reset_ar_enemies()

    def reset_ar_enemies(self):
        """Borra los enemigos normales y crea enemigos 'flotantes'"""
        for e in self.enemies:
            self.remove_widget(e)
        self.enemies.clear()

        # Crear enemigos en un área amplia
        for i in range(8):
            world_x = random.randint(-800, 800)
            world_y = random.randint(300, int(Window.height - 150))
            
            dummy_wp = Waypoint("static", (world_x, world_y))
            enemy = PatrolEnemy([dummy_wp], speed=0)
            
            # Guardar posición virtual
            enemy.world_x = world_x 
            enemy.world_y = world_y
            
            self.enemies.append(enemy)
            self.add_widget(enemy)

    def update(self, dt):
        # 1. Leer sensores
        self.update_camera_offset()

        # 2. Actualizar posición visual de enemigos (Efecto AR)
        center_screen_x = Window.width / 2
        for enemy in self.enemies:
            if not getattr(enemy, 'is_dead', False):
                # Posición pantalla = Centro + (PosMundo - OffsetCámara)
                screen_x = center_screen_x + (enemy.world_x - self.camera_offset_x)
                enemy.center_x = screen_x
                enemy.center_y = enemy.world_y
                enemy.update_sprite()

        # 3. Física y lógica normal
        super().update(dt)

        # Ajuste extra: Asegurar que el fondo negro cubra todo si la ventana cambia
        if hasattr(self, 'bg_black'):
            self.bg_black.size = Window.size

    def update_camera_offset(self):
        if platform == 'android' and accelerometer:
            try:
                val = accelerometer.acceleration[:3]
                if val:
                    accel_x = val[0]
                    if abs(accel_x) > 1.0: 
                        self.camera_offset_x += accel_x * self.sensor_speed
            except:
                pass
        
        # Limites del mundo
        limit = 1000
        if self.camera_offset_x > limit: self.camera_offset_x = limit
        if self.camera_offset_x < -limit: self.camera_offset_x = -limit

    def on_stop(self):
        if platform == 'android':
            try:
                accelerometer.disable()
            except:
                pass
        super().on_stop()
