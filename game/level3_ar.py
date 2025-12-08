import cv2
import numpy as np
import math
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.graphics import Color

# Importamos el nivel base
from game.trajectory_screen import TrajectoryGameScreen

class ARGameScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. Configuración de Cámara con OpenCV
        # Si usas DroidCam, prueba con indices 0, 1 o 2 si no abre a la primera.
        self.capture = cv2.VideoCapture(0) 
        
        # Ajustamos a resolución HD estándar
        self.cam_w = 1280.0
        self.cam_h = 720.0
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)

        # 2. Configuración de ArUco
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

        # 3. Matriz de Cámara Aproximada (para cálculos 3D)
        focal_length = self.cam_w
        center = (self.cam_w / 2, self.cam_h / 2)
        self.camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )
        self.dist_coeffs = np.zeros((4, 1))

        # 4. Widget de Imagen para el fondo (Video en vivo)
        self.camera_image = Image(size=Window.size, allow_stretch=True, keep_ratio=False)
        self.add_widget(self.camera_image)

        # 5. Contenedor "Scatter" para el Mundo del Juego
        # Bloqueamos interacción manual para controlarlo por código
        self.game_container = Scatter(do_rotation=False, do_scale=False, do_translation=False)
        
        # Dimensiones de diseño original
        self.design_width = 540
        self.design_height = 960
        self.game_container.size_hint = (None, None)
        self.game_container.size = (self.design_width, self.design_height)
        self.game_container.center = Window.center
        self.add_widget(self.game_container)

        # ---------------------------------------------------------
        # 6. INSTANCIACIÓN Y PARCHE DEL NIVEL
        # ---------------------------------------------------------
        self.game_level = TrajectoryGameScreen(difficulty="hard")
        
        # A) Borrar fondo del nivel para que sea transparente
        if hasattr(self.game_level, 'bg'):
             self.game_level.canvas.before.remove(self.game_level.bg)
             if hasattr(self.game_level, 'bg_color'):
                 self.game_level.bg_color.a = 0
        
        # B) Sobrescribir el botón "Reintentar" para que recargue AR y no el Nivel 2 normal
        def custom_restart_ar():
            from kivy.app import App
            app = App.get_running_app()
            # Forzamos la recarga del Nivel 3 (AR)
            if hasattr(app, 'start_level3'):
                app.start_level3()
            else:
                print("Error: start_level3 no encontrado en App")

        # Reemplazamos el método de la instancia
        self.game_level.restart_level = custom_restart_ar
        
        # Añadir al contenedor
        self.game_level.size = self.game_container.size
        self.game_container.add_widget(self.game_level)
        # ---------------------------------------------------------

        # 7. UI Informativa
        self.info_label = Label(
            text="[b]APUNTA AL MARCADOR ARUCO (ID 0)[/b]\nEl juego se levantará perpendicularmente",
            markup=True, font_size='24sp', color=(1, 1, 0, 1),
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        self.add_widget(self.info_label)

        # 8. Bucle de actualización (30 FPS)
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)

    def update_frame(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        # Detección de marcadores
        corners, ids, rejected = self.detector.detectMarkers(frame)
        
        detected = False
        if ids is not None:
            for i, marker_id in enumerate(ids):
                # Prioridad al ID 0 o cualquiera disponible
                if marker_id == 0 or len(ids) > 0: 
                    detected = True
                    self.process_marker_3d(corners[i][0], frame)
                    self.info_label.opacity = 0
                    self.game_container.opacity = 1
                    break
        
        if not detected:
            self.info_label.opacity = 1
            # Opcional: Ocultar juego si se pierde tracking
            # self.game_container.opacity = 0.5

        # Renderizar frame en Kivy (Voltear verticalmente y crear textura)
        buf = cv2.flip(frame, 0).tobytes()
        tex = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        tex.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.camera_image.texture = tex
        
        # Actualizar lógica del juego
        self.game_level.update(dt)

    def process_marker_3d(self, corners_2d, frame):
        """Calcula posición, rotación y escala perpendicular al marcador"""
        
        # 1. Definir marcador en 3D
        marker_size = 1.0
        obj_points = np.array([
            [-marker_size/2, marker_size/2, 0], # Top-Left
            [marker_size/2, marker_size/2, 0],  # Top-Right
            [marker_size/2, -marker_size/2, 0], # Bottom-Right
            [-marker_size/2, -marker_size/2, 0] # Bottom-Left
        ], dtype=np.float32)

        corners_2d = np.array(corners_2d, dtype=np.float32)

        # 2. Resolver PnP
        success, rvec, tvec = cv2.solvePnP(obj_points, corners_2d, self.camera_matrix, self.dist_coeffs)
        
        if not success: return

        # FIX CRÍTICO OPCENCV: Forzar formato (3,1) float64
        rvec = np.array(rvec, dtype=np.float64).reshape((3, 1))
        tvec = np.array(tvec, dtype=np.float64).reshape((3, 1))

        # 3. Puntos a proyectar (Base y Cima)
        height_scale_factor = 3.0 # Altura virtual del juego
        axis_points_3d = np.array([
            [0, 0, 0],                      
            [0, 0, marker_size * height_scale_factor] 
        ], dtype=np.float32)

        # 4. Proyectar
        try:
            img_points, _ = cv2.projectPoints(axis_points_3d, rvec, tvec, self.camera_matrix, self.dist_coeffs)
        except cv2.error as e:
            print(f"Error projecting points: {e}")
            return
        
        p_base = img_points[0][0]
        p_top = img_points[1][0]

        # 5. Mapeo a Pantalla Kivy
        screen_w, screen_h = Window.size
        scale_x = screen_w / self.cam_w
        scale_y = screen_h / self.cam_h

        # Invertir Y (OpenCV vs Kivy)
        base_x = p_base[0] * scale_x
        base_y = (self.cam_h - p_base[1]) * scale_y
        
        top_x = p_top[0] * scale_x
        top_y = (self.cam_h - p_top[1]) * scale_y

        # A. Posición (Centro)
        center_x = (base_x + top_x) / 2
        center_y = (base_y + top_y) / 2
        self.game_container.center = (center_x, center_y)

        # B. Rotación (Perpendicular)
        dx = top_x - base_x
        dy = top_y - base_y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        self.game_container.rotation = angle_deg - 90

        # C. Escala
        dist_px = math.hypot(dx, dy)
        if self.design_height > 0:
            scale = dist_px / self.design_height
            self.game_container.scale = scale

    def on_stop(self):
        if self.capture:
            self.capture.release()