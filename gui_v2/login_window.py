from pydantic import ValidationError
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from auth.auth import AuthManager
from gui_v2.config import cfg
from gui_v2.translator import translate
from models.auth_model import UserLoginModel, UserRegModel


# Login window
class LoginWindow(QWidget):
    """Login window widget"""

    # Salt signal
    success = Signal(str)

    def __init__(self):
        super().__init__()

        # Initializing AuthManager
        self.auth_manager = AuthManager()

        # Default layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        self.setContentsMargins(20, 10, 20, 20)
        self.setLayout(main_layout)

        # Top layout
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        # Top button
        self.lang_btn = QPushButton("EN")
        self.lang_btn.setFixedSize(60, 30)
        self.lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #555;
                border-radius: 5px;
                color: #aaa;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #4da3df;
                color: #4da3df;
            }
            """
        )
        self.lang_btn.clicked.connect(self.toggle_language)
        top_layout.addWidget(self.lang_btn)

        main_layout.addLayout(top_layout)

        # Title
        self.title = QLabel("hash.all")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            "font-size: 28px; font-weight: bold; margin-bottom: 10px;"
        )
        main_layout.addWidget(self.title)

        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        # Username
        self.label_username = QLabel()
        self.name_input = QLineEdit()

        # Password
        self.label_password = QLabel()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Add to form layout
        form_layout.addWidget(self.label_username)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.label_password)
        form_layout.addWidget(self.pass_input)

        # Add to main layout
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(15)

        # Buttons
        self.login_btn = QPushButton()
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setStyleSheet("font-weight: bold; font-size: 14px")

        self.register_btn = QPushButton()
        self.register_btn.setMinimumHeight(35)
        self.register_btn.setStyleSheet("background-color: #444444; color: #ccc;")

        # Add to main layout
        main_layout.addWidget(self.login_btn)
        main_layout.addWidget(self.register_btn)

        # Connect logic
        self.login_btn.clicked.connect(self.check_login)
        self.register_btn.clicked.connect(self.register_user)

        # Apply translates at start
        self.retranslate_ui()

    def toggle_language(self):
        """Switches languages between RU and EN"""
        if cfg.data.LANGUAGE == "English":
            cfg.data.LANGUAGE = "Русский"
        else:
            cfg.data.LANGUAGE = "English"

        # Save config and reload translator
        cfg.save()
        translate.load_language()

        # Update UI
        self.retranslate_ui()

    def retranslate_ui(self):
        """Update all texts on window"""
        # Headers
        self.setWindowTitle(translate.get_translation("login_title"))
        self.title.setText(translate.get_translation("login_header"))

        # Labels
        self.label_username.setText(translate.get_translation("login_username_label"))
        self.label_password.setText(translate.get_translation("login_password_label"))

        # Placeholder texts
        self.name_input.setPlaceholderText(
            translate.get_translation("login_username_placeholder")
        )
        self.pass_input.setPlaceholderText(
            translate.get_translation("login_password_placeholder")
        )

        # Buttons
        self.login_btn.setText(translate.get_translation("login_btn"))
        self.register_btn.setText(translate.get_translation("register_btn"))

        # Update text on language button
        current_lang_code = "RU" if cfg.data.LANGUAGE == "Русский" else "EN"
        self.lang_btn.setText(current_lang_code)

    def check_login(self):
        """Сhecks the information received from the fields"""

        username = self.name_input.text()
        password = self.pass_input.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                translate.get_translation("error_title"),
                translate.get_translation("login_error_empty"),
            )
            return

        try:
            login_data = UserLoginModel(username=username, password=password)
            response = self.auth_manager.verify_user(login_data)

            if response.success:
                self.success.emit(response.vault_salt or "")
            else:
                # Login error
                QMessageBox.warning(
                    self,
                    translate.get_translation("login_failed_title"),
                    response.message,
                )
        except ValidationError as e:
            # Error handler, because pydantic v2 giving a detailed description of the error, which is unnecessary here
            error_msg = e.errors()[0]["msg"] if e.errors() else str(e)

            if "Value error" in error_msg:
                error_msg = error_msg.split("Value error,")[1].strip()
            QMessageBox.warning(
                self, translate.get_translation("invalid_data_title"), error_msg
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                translate.get_translation("error_title"),
                translate.get_translation("login_error_unexpected").format(
                    error=str(e)
                ),
            )

    def register_user(self):
        username = self.name_input.text()
        password = self.pass_input.text()

        if not username or not password:
            QMessageBox.warning(
                self,
                translate.get_translation("error_title"),
                translate.get_translation("register_error_empty"),
            )
            return
        try:
            reg_data = UserRegModel(username=username, password=password)

            response = self.auth_manager.register_user(reg_data)

            if response.success:
                QMessageBox.information(
                    self,
                    translate.get_translation("register_success_title"),
                    response.message,
                )
            else:
                QMessageBox.warning(
                    self,
                    translate.get_translation("register_failed_title"),
                    response.message,
                )
        except ValidationError as e:
            # Error handler, because pydantic v2 giving a detailed description of the error, which is unnecessary here
            error_msg = e.errors()[0]["msg"] if e.errors() else str(e)

            if "Value error" in error_msg:
                error_msg = error_msg.split("Value error,")[1].strip()

            error_field = e.errors()[0].get("loc", [""])[0] if e.errors() else ""
            if error_field == "password" or "Password" in error_msg:
                pwd_warning_raw = translate.get_translation("register_warning_password")

                try:
                    error_msg = pwd_warning_raw.format(
                        min_len=cfg.data.MIN_PASSWORD_LENGTH
                    )
                except KeyError:
                    error_msg = pwd_warning_raw

            QMessageBox.warning(
                self, translate.get_translation("invalid_data_title"), error_msg
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                translate.get_translation("error_title"),
                translate.get_translation("register_error_generic").format(
                    error=str(e)
                ),
            )
