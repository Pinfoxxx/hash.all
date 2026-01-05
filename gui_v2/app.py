import sys

from PySide6.QtWidgets import QApplication

from gui_v2.styles import STYLES
from gui_v2.login_window import LoginWindow
from gui_v2.main_window import MainWindow


# Main runtime
class Runtime:
    def __init__(self):
        # Initializing application and applying stylesheets
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(STYLES)

        # Initializing login window and waiting success signal
        self.login_window = LoginWindow()
        self.login_window.success.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self):
        # Closing login window and show main window
        self.login_window.close()
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec())
