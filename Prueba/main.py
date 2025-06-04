from PyQt5.QtWidgets import QApplication
from start_screen import StartScreen
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_screen = StartScreen()
    start_screen.show()
    sys.exit(app.exec_())