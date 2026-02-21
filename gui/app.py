import sys

from PySide6.QtWidgets import QApplication

from gui_v2.styles import STYLES
from gui_v2.main_window import MainWindow


# Main runtime
class Runtime:
    def __init__(self):
        # Initializing application and applying stylesheets
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(STYLES)

        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec())
