# ========================================
# PANTALLA DE JUEGO - RULETA DE SELECCIÓN
# ========================================
# Esta clase maneja la pantalla del juego de ruleta donde:
# - Se muestra una ruleta interactiva con diferentes juegos
# - El usuario puede girar la ruleta para seleccionar un juego al azar
# - Se muestran los personajes y descripciones de los juegos
# - Se puede regresar a la pantalla principal

# Importaciones de PyQt5 para elementos gráficos avanzados
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QHBoxLayout, QGraphicsView, QGraphicsScene, QPushButton, QVBoxLayout, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF, QTimer           # Clases core: puntos, temporizadores
from PyQt5.QtGui import (QPainter, QPolygonF, QBrush, QColor, QPen, QPainterPath, 
                        QPixmap, QTransform, QLinearGradient, QFont)  # Clases de dibujo y gráficos
import math                                            # Matemáticas para cálculos trigonométricos
import random                                          # Generación de números aleatorios
import os                                             # Operaciones del sistema de archivos

# ========================================
# CLASE PRINCIPAL - PANTALLA DE JUEGO DE RULETA
# ========================================
class GameScreen(QMainWindow):
    def __init__(self, start_screen_ref):
        """
        Constructor de la pantalla de juego
        Args:
            start_screen_ref: Referencia a la pantalla de inicio para poder regresar
        """
        # Guardar la referencia a la pantalla de inicio
        self.start_screen = start_screen_ref
        super().__init__()
        
        # ========================================
        # CONFIGURACIÓN BÁSICA DE LA VENTANA
        # ========================================
        self.setWindowTitle("Game Selection")     # Título de la ventana
        self.setFixedSize(1200, 600)             # Tamaño fijo más ancho para la ruleta
        self.setStyleSheet("background-color: #0000FF;")  # Fondo azul
        
        # ========================================
        # CONFIGURACIÓN DEL LAYOUT PRINCIPAL
        # ========================================
        # Crear widget central y layout horizontal principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(50)  # Espacio entre columnas izquierda y derecha
        
        # ========================================
        # CONFIGURACIÓN DE LA COLUMNA IZQUIERDA (RULETA)
        # ========================================
        # Widget contenedor para la ruleta y botón
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Configuración del widget gráfico para la ruleta
        self.wheel_widget = QGraphicsView()
        self.wheel_widget.setFixedSize(550, 550)   # Tamaño fijo para la ruleta
        self.wheel_widget.setStyleSheet("background: transparent; border: none;")
        # Deshabilitar barras de scroll
        self.wheel_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wheel_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Crear escena gráfica para dibujar la ruleta
        self.scene = QGraphicsScene()
        self.wheel_widget.setScene(self.scene)
        left_layout.addWidget(self.wheel_widget)
        
        # Botón para girar la ruleta
        random_button = QPushButton("Random Game")
        random_button.setFixedSize(150, 40)
        random_button.setStyleSheet("background-color: black; color: white; font-size: 14px;")
        random_button.clicked.connect(self.spin_wheel)  # Conectar con función de giro
        left_layout.addWidget(random_button, alignment=Qt.AlignCenter)
        
        # ========================================
        # CONFIGURACIÓN DE LA COLUMNA DERECHA (INFORMACIÓN)
        # ========================================
        # Widget contenedor para mostrar información del juego seleccionado
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Etiqueta para mostrar el personaje y información del juego
        self.character_label = QLabel()
        self.character_label.setFixedSize(400, 400)    # Tamaño fijo para la información
        self.character_label.setAlignment(Qt.AlignCenter)
        self.character_label.setStyleSheet("background: transparent;")
        right_layout.addWidget(self.character_label)
        
        # Agregar widgets al layout principal
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        # ========================================
        # VARIABLES DE CONTROL DEL GIRO
        # ========================================
        self.current_angle = 0          # Ángulo actual de rotación de la ruleta
        self.spin_timer = QTimer()      # Temporizador para animar el giro
        self.spin_timer.timeout.connect(self.update_spin)  # Conectar con función de actualización
        self.spinning = False           # Flag para controlar si está girando
        
        # Crear la ruleta inicial
        # Crear la ruleta inicial
        self.create_wheel()

    # ========================================
    # FUNCIÓN DE CIERRE DE VENTANA
    # ========================================
    def closeEvent(self, event):
        """
        Sobrescribe el evento de cierre para mostrar StartScreen antes de cerrar
        Esta función se ejecuta automáticamente cuando se cierra la ventana
        """
        if self.start_screen:
            self.start_screen.show()  # Mostrar la pantalla de inicio
        super().closeEvent(event)     # Proceder con el cierre de esta ventana
        self.start_screen = None      # Limpiar la referencia a StartScreen

    # ========================================
    # FUNCIÓN PARA CREAR LA RULETA
    # ========================================
    def create_wheel(self):
        """
        Crea la rueda de juegos con segmentos, textos y flecha indicadora
        Cada segmento tiene:
        - Un color distintivo
        - Un texto con el nombre del juego
        - Una imagen de personaje asociada
        - Eventos de hover para mostrar información
        """
        # Establecer fondo transparente para la escena
        self.scene.setBackgroundBrush(Qt.transparent)
        
        # ========================================
        # CONFIGURACIÓN BÁSICA DE LA RULETA
        # ========================================
        center = QPointF(275, 275)  # Centro de la ruleta
        radius = 250                # Radio de la ruleta
        
        # Dibujar círculo base de la ruleta
        self.scene.addEllipse(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2,
            QPen(Qt.black, 2),      # Borde negro
            QBrush(Qt.white)        # Fondo blanco
        )
        
        # ========================================
        # DEFINICIÓN DE JUEGOS Y SUS PROPIEDADES
        # ========================================
        self.games = [
            {"name": "Mario", "color": QColor(255, 0, 0), "character": "mario.png", "description": "Juego de plataformas"},
            {"name": "Tetris", "color": QColor(0, 255, 255), "character": "tetris.png", "description": "Juego de bloques"},
            {"name": "Sonic", "color": QColor(0, 0, 255), "character": "sonic.png", "description": "Juego de velocidad"},
            {"name": "Street Fighter", "color": QColor(255, 165, 0), "character": "fighter.png", "description": "Juego de lucha"},
            {"name": "Pacman", "color": QColor(255, 255, 0), "character": "pacman.png", "description": "Juego de laberinto"},
            {"name": "Space Invader", "color": QColor(0, 255, 0), "character": "spaceinvader.png", "description": "Juego de disparos"}
        ]
        
        # Calcular el ángulo de cada segmento
        angle = 360 / len(self.games)
        
        # ========================================
        # CREACIÓN DE SEGMENTOS DE LA RULETA
        # ========================================
        self.wheel_group = []  # Lista para almacenar todos los elementos de la ruleta
        
        for i, game in enumerate(self.games):
            start_angle = i * angle  # Ángulo de inicio del segmento
            
            path = QPainterPath()
            path.moveTo(center)
            path.arcTo(
                center.x() - radius,
                center.y() - radius,
                radius * 2,
                radius * 2,
                start_angle,
                angle
            )
            path.lineTo(center)
            
            segment = self.scene.addPath(
                path,
                QPen(Qt.black, 2),
                QBrush(game["color"])
            )
            segment.setAcceptHoverEvents(True)
            segment.game = game
            segment.setZValue(1)  # Segmentos en capa 1
            self.wheel_group.append(segment)
            
            def hoverEnterEvent(event, g=game):
                self.show_character(g)
            segment.hoverEnterEvent = hoverEnterEvent
            
            # ========================================
            # CONFIGURACIÓN DEL TEXTO DEL SEGMENTO
            # ========================================
            # Calcular posición para el texto en el centro del segmento
            text_angle_rad = start_angle + (angle / 2)      # Ángulo medio del segmento
            text_radius_pos = radius * 0.5                  # Radio para posición del texto
            text_x_pos = center.x() + text_radius_pos * math.cos(math.radians(text_angle_rad))
            text_y_pos = center.y() + text_radius_pos * math.sin(math.radians(text_angle_rad))
            
            # Crear el elemento de texto
            text_item = QGraphicsTextItem(game["name"])
            text_item.setDefaultTextColor(Qt.white)
            text_item.setFont(QFont("Arial", 12, QFont.Bold))
            current_text_boundingRect = text_item.boundingRect()
            
            # ========================================
            # FONDO PARA EL TEXTO (MEJOR LEGIBILIDAD)
            # ========================================
            # Crear fondo semitransparente para el texto
            text_outline = self.scene.addRect(
                current_text_boundingRect,
                QPen(Qt.black, 1),              # Borde negro
                QBrush(QColor(0, 0, 0, 100))    # Fondo negro semitransparente
            )
            text_outline.setZValue(2)           # Capa 2 para fondos
            
            # Añadir el texto a la escena (ahora que el fondo está detrás)
            self.scene.addItem(text_item)
            text_item.setZValue(3)  # Texto en capa 3 (encima del fondo)
            
            # Ajustar la orientación del conjunto texto+fondo
            display_angle = text_angle_rad
            if text_angle_rad > 90 and text_angle_rad < 270:
                display_angle += 180
            
            # Transformación común para centrar y rotar el texto y su fondo
            common_transform = QTransform()
            common_transform.translate(text_x_pos, text_y_pos) # Mover al punto en la rueda
            common_transform.rotate(display_angle) # Rotar para legibilidad
            # Centrar el conjunto basado en el boundingRect del texto
            common_transform.translate(-current_text_boundingRect.width()/2, -current_text_boundingRect.height()/2)
            
            text_item.setTransform(common_transform)
            text_outline.setTransform(common_transform)
            
            self.wheel_group.append(text_outline)
            self.wheel_group.append(text_item)
        
        # ========================================
        # CREACIÓN DE LA FLECHA INDICADORA
        # ========================================
        # Crear flecha que apunta hacia arriba para indicar selección
        arrow_path = QPainterPath()
        arrow_path.moveTo(275, 65)  # Punto superior
        arrow_path.lineTo(295, 25)  # Punto derecho
        arrow_path.lineTo(255, 25)  # Punto izquierdo
        arrow_path.lineTo(275, 65)  # Volver al punto superior
        
        # Agregar flecha a la escena
        self.arrow = self.scene.addPath(
            arrow_path,
            QPen(Qt.black, 2),      # Borde negro
            QBrush(Qt.black)        # Relleno negro
        )
        self.arrow.setZValue(4)     # Capa superior para asegurar visibilidad
    
    
    # ========================================
    # FUNCIÓN PARA INICIAR EL GIRO DE LA RULETA
    # ========================================
    def spin_wheel(self):
        """
        Inicia el giro de la rueda al hacer clic en el botón "Random Game"
        Características del giro:
        - La rueda gira durante 4 segundos
        - Gira en incrementos de 15 grados cada 30 ms
        - Al finalizar, determina qué juego fue seleccionado
        - Muestra la información del juego seleccionado
        """
        if not self.spinning:
            self.spinning = True                    # Marcar que está girando
            self.spin_timer.start(30)              # Iniciar timer cada 30ms
            QTimer.singleShot(4000, self.stop_spin)  # Detener después de 4 segundos

    # ========================================
    # FUNCIÓN DE ACTUALIZACIÓN DEL GIRO
    # ========================================
    def update_spin(self):
        """
        Actualiza la rotación de la rueda durante el giro
        Se ejecuta cada 30ms mientras la ruleta está girando
        - Incrementa el ángulo de rotación
        - Aplica transformaciones a todos los segmentos
        - Mantiene el texto legible durante la rotación
        """
        self.current_angle += 15  # Incrementar ángulo de rotación
        
        # Definir constantes para el centro y radio de posicionamiento del texto
        center_x, center_y = 275, 275
        text_placement_radius = 250 * 0.5  # Radio para la posición del texto
        
        # ========================================
        # ROTACIÓN DE SEGMENTOS Y ELEMENTOS
        # ========================================
        # Iterar a través de todos los elementos (cada set: segmento, fondo, texto)
        for i in range(0, len(self.wheel_group), 3):  # Paso de 3 debido a [segmento, fondo, texto]
            segment = self.wheel_group[i]
            
            # Aplicar transformación de rotación al segmento
            segment_transform = QTransform()
            segment_transform.translate(center_x, center_y)    # Mover al centro de la ruleta
            segment_transform.rotate(self.current_angle)       # Rotar con la ruleta
            segment_transform.translate(-center_x, -center_y)  # Mover de vuelta
            segment.setTransform(segment_transform)
            
            # ========================================
            # ACTUALIZACIÓN DE TEXTO Y FONDO
            # ========================================
            # Verificar que existan elementos de texto y fondo para este segmento
            if i + 2 < len(self.wheel_group):
                text_outline_item = self.wheel_group[i+1]  # Elemento de fondo
                text_item = self.wheel_group[i+2]          # Elemento de texto
                
                # Calcular parámetros para posicionamiento del texto
                angle_per_segment = 360 / len(self.games)
                game_index = i // 3  # Índice del juego basado en la tripleta
                
                # Calcular ángulo actual del texto en la rueda (incluyendo rotación)
                current_text_angle_on_wheel = (game_index * angle_per_segment) + (angle_per_segment / 2) + self.current_angle
                
                # Calcular nueva posición del texto en la escena
                text_x_scene = center_x + text_placement_radius * math.cos(math.radians(current_text_angle_on_wheel))
                text_y_scene = center_y + text_placement_radius * math.sin(math.radians(current_text_angle_on_wheel))
                
                # Determinar ángulo de rotación del texto para mantenerlo legible
                text_display_rotation = current_text_angle_on_wheel % 360
                if text_display_rotation > 90 and text_display_rotation < 270:
                    text_display_rotation += 180  # Girar 180° si está "boca abajo"
                
                # Aplicar transformaciones al texto y su fondo
                common_text_transform = QTransform()
                common_text_transform.translate(text_x_scene, text_y_scene)  # Mover al punto en la rueda
                common_text_transform.rotate(text_display_rotation)          # Rotar para legibilidad
                # Centrar basado en el tamaño del texto
                common_text_transform.translate(-text_item.boundingRect().width()/2, -text_item.boundingRect().height()/2)
                
                # Aplicar la misma transformación al texto y su fondo
                text_item.setTransform(common_text_transform)
                text_outline_item.setTransform(common_text_transform)

    # ========================================
    # FUNCIÓN PARA DETENER EL GIRO Y SELECCIONAR JUEGO
    # ========================================
    def stop_spin(self):
        """
        Detiene el giro de la rueda y determina el juego seleccionado
        Proceso de selección:
        - Calcula el ángulo final de rotación
        - Determina qué segmento está apuntando la flecha (270°)
        - Muestra información del juego seleccionado
        - Incluye información de debug en consola
        """
        self.spinning = False  # Marcar que ya no está girando
        self.spin_timer.stop()  # Detener el temporizador de animación

        # ========================================
        # CÁLCULOS DE SELECCIÓN DEL JUEGO
        # ========================================
        num_games = len(self.games)
        if num_games == 0:
            return  # No hay juegos para seleccionar

        segment_angle_span = 360.0 / num_games  # Ángulo que ocupa cada segmento

        # Normalizar ángulo actual para estar entre 0-360
        final_rotation_angle = self.current_angle % 360.0
        if final_rotation_angle < 0:
            final_rotation_angle += 360.0

        # La flecha apunta a 270 grados (parte superior de la vista)
        # Calcular qué ángulo de la rueda original está ahora en la marca de 270°
        # Si la rueda rotó X grados en sentido horario, la parte que ahora está en 270° 
        # originalmente estaba en (270 + X)
        angle_at_arrow_on_original_wheel = ((270.0 - final_rotation_angle) % 360.0 + 360.0) % 360.0

        # Determinar el índice del juego seleccionado
        selected_index = int(angle_at_arrow_on_original_wheel / segment_angle_span)
        
        # Asegurar que el índice esté dentro de los límites
        selected_index = max(0, min(selected_index, num_games - 1))

        selected_game = self.games[selected_index]

        # ========================================
        # INFORMACIÓN DE DEBUG (OPCIONAL)
        # ========================================
        print(f"--- Stop Spin Debug ---")
        print(f"Final Wheel Rotation (self.current_angle): {self.current_angle:.2f}")
        print(f"Normalized Final Rotation (final_rotation_angle): {final_rotation_angle:.2f}")
        print(f"Angle on Original Wheel at Arrow (angle_at_arrow_on_original_wheel): {angle_at_arrow_on_original_wheel:.2f}")
        print(f"Segment Angle Span: {segment_angle_span:.2f}")
        print(f"Calculated Selected Index: {selected_index}")
        print(f"Selected Game Name (from self.games[selected_index]): {selected_game['name']}")
        print(f"--- End Debug ---")
        
        # ========================================
        # MOSTRAR INFORMACIÓN DEL JUEGO SELECCIONADO
        # ========================================
        self.character_label.clear()  # Limpiar información anterior
        self.show_character(selected_game)  # Mostrar nuevo juego seleccionado

    # ========================================
    # FUNCIÓN PARA MOSTRAR INFORMACIÓN DEL PERSONAJE/JUEGO
    # ========================================
    def show_character(self, game):
        """
        Muestra la información completa del juego seleccionado
        Incluye:
        - Imagen del personaje/juego
        - Nombre del juego
        - Descripción del juego
        - Manejo de errores si no se encuentra la imagen
        """
        # ========================================
        # CREACIÓN DEL WIDGET CONTENEDOR
        # ========================================
        # Crear widget principal para contener toda la información
        character_widget = QWidget()
        character_layout = QVBoxLayout(character_widget)
        
        # ========================================
        # CONFIGURACIÓN DE LA IMAGEN
        # ========================================
        # Crear etiqueta para mostrar la imagen del personaje
        image_label = QLabel()
        image_path = os.path.join(os.path.dirname(__file__), 'images', game["character"])
        
        # Verificar si la imagen existe y cargarla
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Escalar imagen manteniendo proporciones
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
        else:
            # Mostrar mensaje de error si no se encuentra la imagen
            image_label.setText(f"Image not found:\n{game['character']}")
            image_label.setAlignment(Qt.AlignCenter)
        
        # ========================================
        # CONFIGURACIÓN DEL TEXTO DEL JUEGO
        # ========================================
        # Crear etiqueta para el nombre del juego
        name_label = QLabel(game["name"])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(QFont("Arial", 18, QFont.Bold))
        name_label.setStyleSheet("color: white;")
        
        # Crear etiqueta para la descripción del juego
        desc_label = QLabel(game["description"])
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 14))
        desc_label.setStyleSheet("color: white;")
        
        # ========================================
        # ORGANIZACIÓN DEL LAYOUT
        # ========================================
        # Agregar todos los widgets al layout
        character_layout.addWidget(image_label)
        character_layout.addWidget(name_label)
        character_layout.addWidget(desc_label)
        
        # ========================================
        # ACTUALIZACIÓN DEL DISPLAY
        # ========================================
        # Limpiar el layout anterior si existe
        if self.character_label.layout():
            # Eliminar todos los widgets del layout anterior
            while self.character_label.layout().count():
                item = self.character_label.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            # Crear un nuevo layout si no existe
            self.character_label.setLayout(QVBoxLayout())
        
        # Agregar el nuevo widget al layout principal
        self.character_label.layout().addWidget(character_widget)