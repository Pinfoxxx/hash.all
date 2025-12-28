from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)


# Login window
class LoginWindow(QWidget):
    "Login Window"

    success = Signal()

    def __init__(self):
        super().__init__()

        # Root
        self.setWindowTitle("hash.all")
        self.setFixedSize(400, 350)

        # Default layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        # Title
        title = QLabel("hash.all")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px")
        layout.addWidget(title)

        # Input lines
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Username")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)

        # Buttons
        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("background-color: #555555")

        # Specific layouts
        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.pass_input)
        layout.addSpacing(10)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        def check_login(self):
            username = self.name_input.text()
            password = self.pass_input.text()

            ######################################################
            ## The function from auth will be connected here ##
            ######################################################

            if username and password:
                self.success.emit()
            else:
                QMessageBox.warning(self, "Error", "Please enter username and password")

            def register_user(self):
                print("Pressed register button")
                QMessageBox.information(
                    self, "Register", "placeholder for registation logic"
                )  # The logic from auth will be here
