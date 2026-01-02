import sys

from PySide6.QtWidgets import QApplication

from styles import STYLES
from login_window import LoginWindow
from main_window import MainWindow


# Main runtime
class Runtime:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(STYLES)

        self.login_window = LoginWindow()
        self.login_window.show()

    def show_main_app(self):
        self.login_window.close()
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    process = Runtime()
    process.run()
