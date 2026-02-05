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

from pass_gen.pass_gen import PasswordGen
from web_requests.russian_api.hash_search import HashDBSearch


class GeneratorTab(QWidget):
    # Signal for password vault
    password_used_in_vault = Signal(str)

    def __init__(self):
        super().__init__()
        # Default layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Grid generation
        grid = QGridLayout()

        # Spinbox
        self.spin = QSpinBox()
        self.spin.setRange(4, 128)
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
        self.input.setStyleSheet("font-size: 16px; font-weight: bold; color: #4da3df;")
        layout.addWidget(self.input)

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

        # Russian database (debug-only)
        self.ru_db = HashDBSearch("https://disk.yandex.ru/d/O22Pp0Anlf0rRA")

        # Linking events
        self.generate.clicked.connect(self.generate_password)
        self.copy.clicked.connect(self.copy_to_clipboard)
        self.vault.clicked.connect(self.on_use_in_vault)

    def generate_password(self):
        "Generate password"
        lenght = self.spin.value()
        opts = {
            "use_upper": self.cb_upper.isChecked(),
            "use_lower": self.cb_lower.isChecked(),
            "use_digits": self.cb_digits.isChecked(),
            "use_special": self.cb_special.isChecked(),
        }

        try:
            password = PasswordGen.generate(
                lenght=lenght, **opts
            )  # Giving all arguments

            self.input.setText(password)

        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def copy_to_clipboard(self):
        "Copy to clipboard"
        if self.input.text():
            QApplication.clipboard().setText(self.input.text())
        else:
            QMessageBox.warning(self, "Warning", "Nothing to copy!")

    def on_use_in_vault(self):
        "Send password to main window for save in vault"
        password = self.input.text()
        if password:
            self.password_used_in_vault.emit(password)
        else:
            QMessageBox.warning(self, "Warning", "Generate a password first!")
