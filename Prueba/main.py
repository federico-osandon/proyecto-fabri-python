
# ========================================
# ARCHIVO PRINCIPAL - PUNTO DE ENTRADA
# ========================================
# Este archivo inicializa y ejecuta la aplicación principal del arcade de juegos
# Funciones principales:
# - Crear la aplicación PyQt5
# - Mostrar la pantalla de inicio
# - Ejecutar el bucle principal de eventos

# Importaciones necesarias para la aplicación GUI
from PyQt5.QtWidgets import QApplication  # Clase principal para aplicaciones PyQt5
from start_screen import StartScreen      # Pantalla de inicio del arcade
import sys                               # Módulo del sistema para argumentos y salida

# ========================================
# PUNTO DE ENTRADA PRINCIPAL
# ========================================
if __name__ == '__main__':
    # Crear la aplicación PyQt5 con argumentos de línea de comandos
    app = QApplication(sys.argv)
    
    # Crear la ventana de pantalla de inicio
    start_screen = StartScreen()
    
    # Mostrar la ventana principal
    start_screen.show()
    
    # Ejecutar el bucle principal de eventos y salir cuando se cierre
    sys.exit(app.exec_())