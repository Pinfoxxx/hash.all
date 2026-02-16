from pydantic import ValidationError
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auth.auth import AuthManager
from models.auth_model import UserLoginModel, UserRegModel


# Login window
class LoginWindow(QWidget):
    "Login window widget"

    success = Signal()

    def __init__(self):
        super().__init__()

        # Initializing AuthManager
        self.auth_manager = AuthManager()

        # Root
        self.setWindowTitle("hash.all")
        self.setFixedSize(400, 350)

        # Default layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # Title
        title = QLabel("hash.all")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px")
        layout.addWidget(title)

        # Input lines
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Username")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Buttons
        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("background-color: #555555")

        self.login_button.clicked.connect(self.check_login)
        self.register_button.clicked.connect(self.register_user)

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

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return

        try:
            login_data = UserLoginModel(username=username, password=password)

            response = self.auth_manager.verify_user(login_data)

            if response.success:
                self.success.emit()
            else:
                # Login error
                QMessageBox.warning(self, "Login Failed", response.message)
        except ValidationError as e:
            # Error handler, because pydantic v2 giving a detailed description of the error, which is unnecessary here
            error_msg = e.errors()[0]["msg"] if e.errors() else str(e)

            if "Value error" in error_msg:
                error_msg = error_msg.split("Value error,")[1].strip()
            QMessageBox.warning(self, "Invalid Data", error_msg)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An unexpected error occurred: {str(e)}"
            )

    def register_user(self):
        username = self.name_input.text()
        password = self.pass_input.text()

        if not username or not password:
            QMessageBox.warning(
                self, "Error", "Please enter username and password to register"
            )
            return
        try:
            reg_data = UserRegModel(username=username, password=password)

            response = self.auth_manager.register_user(reg_data)

            if response.success:
                QMessageBox.information(self, "Success", response.message)
            else:
                QMessageBox.warning(self, "Registration Failed", response.message)
        except ValidationError as e:
            # Error handler, because pydantic v2 giving a detailed description of the error, which is unnecessary here
            error_msg = e.errors()[0]["msg"] if e.errors() else str(e)

            if "Value error" in error_msg:
                error_msg = error_msg.split("Value error,")[1].strip()

            QMessageBox.warning(self, "Invalid Data", error_msg)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration error: {str(e)}")
