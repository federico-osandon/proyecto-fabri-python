from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from game_screen import GameScreen
import os
import sys
import subprocess

class StartScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Retro Arcade")
        self.setFixedSize(800, 600)
        
        # Set white background
        self.setStyleSheet("background-color: white;")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create ARCADEOG label
        start_label = QLabel("ARCADEOG")
        start_label.setAlignment(Qt.AlignCenter)
        start_label.setFont(QFont('Arial', 48, QFont.Bold))
        start_label.setStyleSheet("color: black;")  # Cambiar color de texto a negro para que contraste con fondo blanco
        
        # Create "Elegir Juego (Ruleta)" button
        wheel_game_button = QPushButton("Ruleta")
        wheel_game_button.setFixedSize(300, 60)
        wheel_game_button.setFont(QFont('Arial', 20))
        wheel_game_button.setStyleSheet("background-color: white; color: black; border: 2px solid black; border-radius: 5px;")
        wheel_game_button.clicked.connect(self.show_game_screen)

        # Create "Tetris" button
        tetris_button = QPushButton("Tetris")
        tetris_button.setFixedSize(300, 60)
        tetris_button.setFont(QFont('Arial', 20))
        tetris_button.setStyleSheet("background-color: white; color: black; border: 2px solid black; border-radius: 5px;")
        tetris_button.clicked.connect(self.start_tetris_game)
        
        # Add widgets to layout
        layout.addStretch()
        layout.addWidget(start_label)
        layout.addSpacing(40)
        layout.addWidget(wheel_game_button, alignment=Qt.AlignCenter)
        layout.addSpacing(20)  # Spacing between buttons
        layout.addWidget(tetris_button, alignment=Qt.AlignCenter)
        layout.addStretch()

    def show_game_screen(self):
        # Pasa 'self' (la instancia de StartScreen) a GameScreen
        self.game_screen = GameScreen(self)  
        self.game_screen.show()
        self.hide()  # Ocultar StartScreen

    def start_tetris_game(self):
        try:
            self.hide()
            tetris_path = os.path.join(os.path.dirname(__file__), 'tetris.py')
            python_executable = sys.executable
            if not python_executable: # Fallback
                python_executable = "python"

            if sys.platform == 'win32':
                # Usar shell=True puede ser necesario en Windows para encontrar python en el PATH
                # y para que la ventana de Pygame no se cierre inmediatamente si hay un error de importación en tetris.py
                process = subprocess.Popen([python_executable, tetris_path], shell=True)
            else:
                process = subprocess.Popen([python_executable, tetris_path])
            process.wait()  # Esperar a que el proceso de Tetris termine
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar Tetris: {str(e)}")
        finally:
            self.show() # Asegurarse de que la ventana principal se muestre de nuevo