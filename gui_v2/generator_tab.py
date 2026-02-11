from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui_v2.config import cfg
from pass_gen.pass_gen import PasswordGen
from web_requests.hibp_api import HIBPClient
from web_requests.russian_api.hash_search import HashDBSearch


class GeneratorTab(QWidget):
    # Signal for password vault
    password_used_in_vault = Signal(str)

    def __init__(self):
        super().__init__()

        # Initializing APIs
        self.hibp_api = HIBPClient()
        self.ru_db = HashDBSearch()
        # Initializing gui
        self.init_ui()

    def init_ui(self):
        # Default layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Grid generation
        grid = QGridLayout()

        # Spinbox
        self.spin = QSpinBox()
        self.spin.setRange(cfg.data.MIN_PASSWORD_LENGTH, cfg.data.MAX_PASSWORD_LENGTH)
        self.spin.setValue(16)

        # Checkboxes
        self.cb_upper = QCheckBox("Uppercase letters (A-Z)")
        self.cb_upper.setChecked(True)
        self.cb_lower = QCheckBox("Lowercase letters (a-z)")
        self.cb_lower.setChecked(True)
        self.cb_digits = QCheckBox("Digits (0-9)")
        self.cb_digits.setChecked(True)
        self.cb_special = QCheckBox("Special characters (!@#$%)")
        self.cb_special.setChecked(True)

        # Grid settings
        grid.addWidget(QLabel("Password lenght:"), 0, 0)
        grid.addWidget(self.spin, 0, 1)
        grid.addWidget(self.cb_upper, 1, 0)
        grid.addWidget(self.cb_lower, 2, 0)
        grid.addWidget(self.cb_digits, 3, 0)
        grid.addWidget(self.cb_special, 4, 0)

        # Add grid to default layout
        layout.addLayout(grid)
        layout.addSpacing(20)

        # Generated passwords widget
        layout.addWidget(QLabel("Generated password:"))
        self.input = QLineEdit()
        self.input.setReadOnly(True)
        self.input.setPlaceholderText("There will be a password here...")
        layout.addWidget(self.input)

        # Check status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)

        # Checkbox for bypass
        self.bypass = QCheckBox("Use Russian bypass")
        layout.addWidget(self.bypass)

        # Buttons
        buttons = QHBoxLayout()
        self.generate = QPushButton("Generate password")
        self.copy = QPushButton("Copy to clipboard")
        self.vault = QPushButton("Use in vault")

        # Buttons layout
        buttons.addWidget(self.generate)
        buttons.addWidget(self.copy)
        buttons.addWidget(self.vault)

        # Add buttons to default layout
        layout.addLayout(buttons)
        layout.addStretch()

        # Linking events
        self.generate.clicked.connect(self.generation_handler)
        self.copy.clicked.connect(self.copy_to_clipboard)
        self.vault.clicked.connect(self.on_use_in_vault)

    def generation_handler(self):
        "Generate password"

        try:
            password = PasswordGen.generate(
                length=self.spin.value(),
                use_upper=self.cb_upper.isChecked(),
                use_lower=self.cb_lower.isChecked(),
                use_digits=self.cb_digits.isChecked(),
                use_special=self.cb_special.isChecked(),
            )  # Giving all arguments
        except ValueError as e:
            self.status_label.setText(f"Error: {e}")
            return

        self.input.setText(password)
        self.status_label.setText("🔍 Checking database, please wait...")
        self.status_label.setStyleSheet("color: #4da3df;")

        # Update UI
        QApplication.processEvents()

        # Checking through web requests
        count = 0
        api_name = ""

        try:
            if self.bypass.isChecked():
                # Russian DB
                api_name = "Russian DB"
                if not self.ru_db.is_ready:
                    self.status_label.setText(
                        "⏳ Initializing Russian DB (one-time)..."
                    )
                    QApplication.processEvents()
                    self.ru_db.initialize()
                if self.ru_db.is_ready:
                    count = self.ru_db.check_password(password)
                else:
                    self.status_label.setText("❌  Russian DB is not initialized")
                    self.status_label.setStyleSheet("color: #ff4d4d")
                    return
            else:
                # HIBP API
                api_name = "HIBP API"
                count = self.hibp_api.check_password_breach(password)

            if count == -1:  # Error
                self.status_label.setText(f"⚠️ Connection error with {api_name}")
                self.status_label.setStyleSheet("color: #ffa500")
            elif count > 0:  # No error, but still not good
                self.status_label.setText(
                    f"❌  Found in {count} breaches ({api_name})!"
                )
                self.status_label.setStyleSheet("color:#ff4d4d;")
            else:
                self.status_label.setText(f"✅ Secure (Verified via {api_name})")
                self.status_label.setStyleSheet("color: #2ecc71;")

        except Exception as e:
            self.status_label.setText(f"⚠️ Error: {str(e)}")

    def copy_to_clipboard(self):
        "Copy to clipboard"
        if self.input.text():
            QApplication.clipboard().setText(self.input.text())
            QMessageBox.information(
                self, "Success", "Password successfully copied to clipboard!"
            )

    def on_use_in_vault(self):
        "Send password to main window for save in vault"
        if self.input.text():
            self.password_used_in_vault.emit(self.input.text())
        else:
            QMessageBox.warning(self, "Warning", "Please generate a password first.")
