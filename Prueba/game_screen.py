from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QHBoxLayout, QGraphicsView, QGraphicsScene, QPushButton, QVBoxLayout, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import (QPainter, QPolygonF, QBrush, QColor, QPen, QPainterPath, 
                        QPixmap, QTransform, QLinearGradient, QFont)
import math
import random
import os

class GameScreen(QMainWindow):
    def __init__(self, start_screen_ref):  # Aceptar la referencia a StartScreen
        self.start_screen = start_screen_ref  # Guardar la referencia
        super().__init__()
        self.setWindowTitle("Game Selection")
        self.setFixedSize(1200, 600)
        self.setStyleSheet("background-color: #0000FF;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(50)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignCenter)
        
        self.wheel_widget = QGraphicsView()
        self.wheel_widget.setFixedSize(550, 550)
        self.wheel_widget.setStyleSheet("background: transparent; border: none;")
        self.wheel_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wheel_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene = QGraphicsScene()
        self.wheel_widget.setScene(self.scene)
        left_layout.addWidget(self.wheel_widget)
        
        random_button = QPushButton("Random Game")
        random_button.setFixedSize(150, 40)
        random_button.setStyleSheet("background-color: black; color: white; font-size: 14px;")
        random_button.clicked.connect(self.spin_wheel)
        left_layout.addWidget(random_button, alignment=Qt.AlignCenter)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)
        
        self.character_label = QLabel()
        self.character_label.setFixedSize(400, 400)
        self.character_label.setAlignment(Qt.AlignCenter)
        self.character_label.setStyleSheet("background: transparent;")
        right_layout.addWidget(self.character_label)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        self.current_angle = 0
        self.spin_timer = QTimer()
        self.spin_timer.timeout.connect(self.update_spin)
        self.spinning = False
        
        self.create_wheel()

    def closeEvent(self, event):
        """Sobrescribe el evento de cierre para mostrar StartScreen antes de cerrar."""
        if self.start_screen:
            self.start_screen.show()  # Mostrar la pantalla de inicio
        super().closeEvent(event)  # Proceder con el cierre de esta ventana

        self.start_screen = None  # Limpiar la referencia a StartScreen

    # crea la rueda de juegos con segmentos, textos y flecha
    # Cada segmento tiene un color, un texto y una imagen de personaje
    # La rueda gira al hacer clic en el botón "Random Game"
    def create_wheel(self):
        self.scene.setBackgroundBrush(Qt.transparent)
        
        center = QPointF(275, 275)
        radius = 250
        
        self.scene.addEllipse(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2,
            QPen(Qt.black, 2),
            QBrush(Qt.white)
        )
        
        self.games = [
            {"name": "Mario", "color": QColor(255, 0, 0), "character": "mario.png", "description": "Juego de plataformas"},
            {"name": "Tetris", "color": QColor(0, 255, 255), "character": "tetris.png", "description": "Juego de bloques"},
            {"name": "Sonic", "color": QColor(0, 0, 255), "character": "sonic.png", "description": "Juego de velocidad"},
            {"name": "Street Fighter", "color": QColor(255, 165, 0), "character": "fighter.png", "description": "Juego de lucha"},
            {"name": "Pacman", "color": QColor(255, 255, 0), "character": "pacman.png", "description": "Juego de laberinto"},
            {"name": "Space Invader", "color": QColor(0, 255, 0), "character": "spaceinvader.png", "description": "Juego de disparos"}
        ]
        
        angle = 360 / len(self.games)
        
        self.wheel_group = []
        for i, game in enumerate(self.games):
            start_angle = i * angle
            
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
            
            # Calcular posición para el texto y su fondo
            text_angle_rad = start_angle + (angle / 2)
            text_radius_pos = radius * 0.5 # Radio para la posición del texto
            text_x_pos = center.x() + text_radius_pos * math.cos(math.radians(text_angle_rad))
            text_y_pos = center.y() + text_radius_pos * math.sin(math.radians(text_angle_rad))
            
            # Crear el texto (sin añadir a la escena aún para obtener su bounding rect)
            text_item = QGraphicsTextItem(game["name"])
            text_item.setDefaultTextColor(Qt.white)
            text_item.setFont(QFont("Arial", 12, QFont.Bold))
            current_text_boundingRect = text_item.boundingRect()
            
            # Crear el fondo para el texto (outline)
            text_outline = self.scene.addRect(
                current_text_boundingRect,
                QPen(Qt.black, 1),  # Borde negro para el fondo
                QBrush(QColor(0, 0, 0, 100))  # Fondo negro semitransparente
            )
            text_outline.setZValue(2)  # Fondo en capa 2
            
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
        
        arrow_path = QPainterPath()
        arrow_path.moveTo(275, 65)
        arrow_path.lineTo(295, 25)
        arrow_path.lineTo(255, 25)
        arrow_path.lineTo(275, 65)
        
        self.arrow = self.scene.addPath(
            arrow_path,
            QPen(Qt.black, 2),
            QBrush(Qt.black)
        )
        self.arrow.setZValue(4)  # Asegurar que la flecha esté en la capa superior
    
    
    # Inicia el giro de la rueda al hacer clic en el botón "Random Game"
    # La rueda gira durante 4 segundos y luego se detiene, mostrando el juego seleccionado
    # La rueda gira en incrementos de 15 grados cada 30 ms
    # El juego seleccionado se muestra en la parte derecha de la pantalla
    # El juego seleccionado se muestra con su imagen, nombre y descripción
    # La rueda se detiene en un juego aleatorio, calculando el ángulo de rotación final
    # y determinando qué segmento está en la parte superior (270 grados)
    # La rueda se detiene suavemente, mostrando el juego seleccionado en la parte derecha de la pantalla
    # La rueda se detiene en el segmento que está en la parte superior (270 grados)
    # El juego seleccionado se muestra con su imagen, nombre y descripción
    # La rueda se detiene en un juego aleatorio, calculando el ángulo de rotación final
    # y determinando qué segmento está en la parte superior (270 grados)
    # La rueda se detiene suavemente, mostrando el juego seleccionado en la parte derecha de la pantalla
    # La rueda se detiene en el segmento que está en la parte superior (270 grados)
    def spin_wheel(self):
        if not self.spinning:
            self.spinning = True
            self.spin_timer.start(30)
            QTimer.singleShot(4000, self.stop_spin)

    # Actualiza la rotación de la rueda cada 30 ms
    # Cada segmento se rota 15 grados y se actualiza su posición y orientación
    # El texto de cada segmento se actualiza para que sea legible
    # El texto se coloca en la posición correcta en la rueda y se rota para que sea legible
    # El texto se coloca en la posición correcta en la rueda y se rota para que sea legible
    def update_spin(self):
        self.current_angle += 15
        
        center_x, center_y = 275, 275
        text_placement_radius = 250 * 0.5 # Radio para la posición del texto
        
        # Iterar a través de segmentos, fondos de texto y textos
        for i in range(0, len(self.wheel_group), 3): # Paso de 3 debido a [segmento, fondo, texto]
            segment = self.wheel_group[i]
            
            # Transformación del segmento
            segment_transform = QTransform()
            segment_transform.translate(center_x, center_y) # Mover al centro de la ruleta
            segment_transform.rotate(self.current_angle)    # Rotar con la ruleta
            segment_transform.translate(-center_x, -center_y) # Mover de vuelta
            segment.setTransform(segment_transform)
            
            # Asegurarse de que el fondo y el texto existan para este segmento
            if i + 2 < len(self.wheel_group):
                text_outline_item = self.wheel_group[i+1]
                text_item = self.wheel_group[i+2]
                
                angle_per_segment = 360 / len(self.games)
                game_index = i // 3 # Índice del juego basado en la tripleta
                
                # Ángulo del texto en la rueda, incluyendo la rotación actual
                current_text_angle_on_wheel = (game_index * angle_per_segment) + (angle_per_segment / 2) + self.current_angle
                
                # Calcular la posición (x,y) del centro del texto en la escena
                text_x_scene = center_x + text_placement_radius * math.cos(math.radians(current_text_angle_on_wheel))
                text_y_scene = center_y + text_placement_radius * math.sin(math.radians(current_text_angle_on_wheel))
                
                # Determinar el ángulo de rotación del texto para mantenerlo legible
                text_display_rotation = current_text_angle_on_wheel % 360
                if text_display_rotation > 90 and text_display_rotation < 270:
                    text_display_rotation += 180 # Girar 180 grados si está "boca abajo"
                
                # Transformación común para el texto y su fondo
                common_text_transform = QTransform()
                common_text_transform.translate(text_x_scene, text_y_scene) # Mover al punto en la rueda
                common_text_transform.rotate(text_display_rotation) # Rotar para legibilidad
                # Centrar basado en el boundingRect del texto
                common_text_transform.translate(-text_item.boundingRect().width()/2, -text_item.boundingRect().height()/2)
                
                text_item.setTransform(common_text_transform)
                text_outline_item.setTransform(common_text_transform) # Aplicar la misma transformación al fondo

    # Detiene el giro de la rueda y muestra el juego seleccionado
    # Calcula el ángulo final de rotación y determina qué segmento está en la parte superior (270 grados)
    # El juego seleccionado se muestra con su imagen, nombre y descripción
    # El juego seleccionado se muestra en la parte derecha de la pantalla   
    # La rueda se detiene suavemente, mostrando el juego seleccionado en la parte derecha de la pantalla
    # La rueda se detiene en el segmento que está en la parte superior (270 grados)
    # El juego seleccionado se muestra con su imagen, nombre y descripción
    def stop_spin(self):
        self.spinning = False
        self.spin_timer.stop()

        num_games = len(self.games)
        if num_games == 0:
            return # No games to select

        segment_angle_span = 360.0 / num_games

        # Normalize current_angle to be positive and within 0-360
        final_rotation_angle = self.current_angle % 360.0
        if final_rotation_angle < 0:
            final_rotation_angle += 360.0

        # The arrow points to 270 degrees (top of the view).
        # We need to find which angle on the original wheel is now at this 270-degree mark.
        # If the wheel rotated clockwise by X, the part now at 270 was originally at (270 + X).
        angle_at_arrow_on_original_wheel = ((270.0 - final_rotation_angle) % 360.0 + 360.0) % 360.0

        # Determine the index of the selected game
        selected_index = int(angle_at_arrow_on_original_wheel / segment_angle_span)
        
        # Ensure index is within bounds (it should be by calculation, but as a safeguard)
        selected_index = max(0, min(selected_index, num_games - 1))

        selected_game = self.games[selected_index]

        print(f"--- Stop Spin Debug ---")
        print(f"Final Wheel Rotation (self.current_angle): {self.current_angle:.2f}")
        print(f"Normalized Final Rotation (final_rotation_angle): {final_rotation_angle:.2f}")
        print(f"Angle on Original Wheel at Arrow (angle_at_arrow_on_original_wheel): {angle_at_arrow_on_original_wheel:.2f}")
        print(f"Segment Angle Span: {segment_angle_span:.2f}")
        print(f"Calculated Selected Index: {selected_index}")
        print(f"Selected Game Name (from self.games[selected_index]): {selected_game['name']}")
        print(f"--- End Debug ---")
        
        self.character_label.clear()
        self.show_character(selected_game)

    def show_character(self, game):
        # Crear un widget para contener la imagen y la descripción
        character_widget = QWidget()
        character_layout = QVBoxLayout(character_widget)
        
        # Mostrar la imagen del personaje
        image_label = QLabel()
        image_path = os.path.join(os.path.dirname(__file__), 'images', game["character"])
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
        else:
            image_label.setText(f"Image not found:\n{game['character']}")
            image_label.setAlignment(Qt.AlignCenter)
        
        # Mostrar el nombre y la descripción del juego
        name_label = QLabel(game["name"])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(QFont("Arial", 18, QFont.Bold))
        name_label.setStyleSheet("color: white;")
        
        desc_label = QLabel(game["description"])
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Arial", 14))
        desc_label.setStyleSheet("color: white;")
        
        # Agregar widgets al layout
        character_layout.addWidget(image_label)
        character_layout.addWidget(name_label)
        character_layout.addWidget(desc_label)
        
        # Limpiar el layout anterior y mostrar el nuevo widget
        if self.character_label.layout():
            # Limpiar el layout anterior si existe
            while self.character_label.layout().count():
                item = self.character_label.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            # Crear un nuevo layout si no existe
            self.character_label.setLayout(QVBoxLayout())
        
        self.character_label.layout().addWidget(character_widget)