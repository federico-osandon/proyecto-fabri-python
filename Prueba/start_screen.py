
# ========================================
# PANTALLA DE INICIO DEL ARCADE
# ========================================
# Esta clase maneja la pantalla principal del arcade donde el usuario puede:
# - Ver el título "ARCADEOG"
# - Seleccionar entre diferentes juegos disponibles (Ruleta, Tetris)
# - Navegar a las respectivas pantallas de juego

# Importaciones de PyQt5 para la interfaz gráfica
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt                    # Constantes de Qt (alineación, etc.)
from PyQt5.QtGui import QFont                  # Manejo de fuentes
from game_screen import GameScreen             # Pantalla del juego de ruleta
import os                                      # Operaciones del sistema operativo
import sys                                     # Módulo del sistema
import subprocess                              # Ejecución de procesos externos

# ========================================
# CLASE PRINCIPAL - PANTALLA DE INICIO
# ========================================
class StartScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ========================================
        # CONFIGURACIÓN BÁSICA DE LA VENTANA
        # ========================================
        self.setWindowTitle("Retro Arcade")    # Título de la ventana
        self.setFixedSize(800, 600)            # Tamaño fijo de la ventana
        
        # Establecer fondo blanco para toda la ventana
        self.setStyleSheet("background-color: white;")
        
        # ========================================
        # CONFIGURACIÓN DEL WIDGET CENTRAL Y LAYOUT
        # ========================================
        # Crear widget central (PyQt5 requiere un widget central para QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear layout vertical para organizar los elementos
        layout = QVBoxLayout(central_widget)
        
        # ========================================
        # CREACIÓN DEL TÍTULO PRINCIPAL
        # ========================================
        # Crear etiqueta con el título "ARCADEOG"
        start_label = QLabel("ARCADEOG")
        start_label.setAlignment(Qt.AlignCenter)                    # Centrar texto
        start_label.setFont(QFont('Arial', 48, QFont.Bold))        # Fuente grande y negrita
        start_label.setStyleSheet("color: black;")                # Color negro para contrastar con fondo blanco
        
        # ========================================
        # CREACIÓN DEL BOTÓN DE RULETA
        # ========================================
        # Crear botón para acceder al juego de ruleta
        wheel_game_button = QPushButton("Ruleta")
        wheel_game_button.setFixedSize(300, 60)                    # Tamaño fijo del botón
        wheel_game_button.setFont(QFont('Arial', 20))              # Fuente del botón
        wheel_game_button.setStyleSheet("background-color: white; color: black; border: 2px solid black; border-radius: 5px;")
        # Conectar el botón con la función que muestra la pantalla de juego
        # Conectar el botón con la función que muestra la pantalla de juego
        wheel_game_button.clicked.connect(self.show_game_screen)

        # ========================================
        # CREACIÓN DEL BOTÓN DE TETRIS
        # ========================================
        # Crear botón para acceder al juego Tetris
        tetris_button = QPushButton("Tetris")
        tetris_button.setFixedSize(300, 60)                        # Tamaño fijo del botón
        tetris_button.setFont(QFont('Arial', 20))                  # Fuente del botón
        tetris_button.setStyleSheet("background-color: white; color: black; border: 2px solid black; border-radius: 5px;")
        # Conectar el botón con la función que inicia el juego Tetris
        tetris_button.clicked.connect(self.start_tetris_game)
        
        # ========================================
        # ORGANIZACIÓN DE ELEMENTOS EN EL LAYOUT
        # ========================================
        # Agregar espacio flexible al inicio para centrar verticalmente
        layout.addStretch()
        
        # Agregar el título principal
        layout.addWidget(start_label)
        
        # Agregar espacio entre el título y los botones
        layout.addSpacing(40)
        
        # Agregar botón de ruleta centrado
        layout.addWidget(wheel_game_button, alignment=Qt.AlignCenter)
        
        # Agregar espacio entre botones
        layout.addSpacing(20)
        
        # Agregar botón de Tetris centrado
        layout.addWidget(tetris_button, alignment=Qt.AlignCenter)
        
        # Agregar espacio flexible al final para centrar verticalmente
        # Agregar espacio flexible al final para centrar verticalmente
        layout.addStretch()

    # ========================================
    # FUNCIÓN PARA MOSTRAR LA PANTALLA DE JUEGO DE RULETA
    # ========================================
    def show_game_screen(self):
        """
        Función que se ejecuta cuando se hace clic en el botón "Ruleta"
        - Crea una nueva instancia de GameScreen
        - Pasa la referencia de la pantalla actual (self) para poder regresar
        - Muestra la pantalla de juego
        - Oculta la pantalla de inicio actual
        """
        # Crear nueva instancia de GameScreen pasando referencia de esta pantalla
        self.game_screen = GameScreen(self)  
        # Mostrar la pantalla de juego
        self.game_screen.show()
        # Ocultar la pantalla de inicio actual
        self.hide()

    # ========================================
    # FUNCIÓN PARA INICIAR EL JUEGO TETRIS
    # ========================================
    def start_tetris_game(self):
        """
        Función que se ejecuta cuando se hace clic en el botón "Tetris"
        - Oculta la ventana actual
        - Ejecuta el archivo tetris.py como un proceso separado
        - Maneja errores de ejecución
        - Restaura la ventana cuando Tetris se cierra
        """
        try:
            # Ocultar la ventana actual antes de iniciar Tetris
            self.hide()
            
            # ========================================
            # CONFIGURACIÓN DE LA RUTA DEL ARCHIVO TETRIS
            # ========================================
            # Obtener la ruta completa del archivo tetris.py
            tetris_path = os.path.join(os.path.dirname(__file__), 'tetris.py')
            
            # Obtener el ejecutable de Python actual
            python_executable = sys.executable
            if not python_executable:  # Fallback en caso de que no se encuentre
                python_executable = "python"

            # ========================================
            # EJECUCIÓN DEL PROCESO TETRIS
            # ========================================
            # Configurar la ejecución según el sistema operativo
            if sys.platform == 'win32':
                # En Windows: usar shell=True para encontrar python en el PATH
                # y para que la ventana de Pygame no se cierre inmediatamente si hay error
                process = subprocess.Popen([python_executable, tetris_path], shell=True)
            else:
                # En Linux/macOS: ejecución directa sin shell
                process = subprocess.Popen([python_executable, tetris_path])
            
            # Esperar a que el proceso de Tetris termine antes de continuar
            process.wait()
            
        except Exception as e:
            # ========================================
            # MANEJO DE ERRORES
            # ========================================
            # Mostrar mensaje de error si algo sale mal al iniciar Tetris
            QMessageBox.critical(self, "Error", f"Error al iniciar Tetris: {str(e)}")
        finally:
            # ========================================
            # RESTAURACIÓN DE LA VENTANA PRINCIPAL
            # ========================================
            # Asegurarse de que la ventana principal se muestre de nuevo
            # sin importar si Tetris se ejecutó correctamente o no
            self.show()