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

from gui.config import cfg
from gui.translator import translate
from pass_gen.pass_gen import PasswordGen
from web_requests.hibp_api import HIBPClient
from web_requests.russian_api.hash_search import HashDBSearch


class GeneratorTab(QWidget):
    """Generator tab widget"""

    # Signal for password vault
    password_used_in_vault = Signal(str)

    def __init__(self):
        super().__init__()

        # Initializing APIs
        self.hibp_api = HIBPClient()
        self.ru_db = HashDBSearch()

        # Initializing gui
        self.init_ui()

        # Apply translates at start
        self.retranslate_ui()

    def init_ui(self):
        # Default layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Grid generation
        grid = QGridLayout()

        # Label for length
        self.label_length = QLabel()

        # Spinbox
        self.spin = QSpinBox()
        self.spin.setRange(cfg.data.MIN_PASSWORD_LENGTH, cfg.data.MAX_PASSWORD_LENGTH)
        self.spin.setValue(16)

        # Checkboxes
        self.cb_upper = QCheckBox()
        self.cb_upper.setChecked(True)

        self.cb_lower = QCheckBox()
        self.cb_lower.setChecked(True)

        self.cb_digits = QCheckBox()
        self.cb_digits.setChecked(True)

        self.cb_special = QCheckBox()
        self.cb_special.setChecked(True)

        # Grid settings
        grid.addWidget(self.label_length, 0, 0)
        grid.addWidget(self.spin, 0, 1)
        grid.addWidget(self.cb_upper, 1, 0)
        grid.addWidget(self.cb_lower, 2, 0)
        grid.addWidget(self.cb_digits, 3, 0)
        grid.addWidget(self.cb_special, 4, 0)

        # Add grid to default layout
        layout.addLayout(grid)
        layout.addSpacing(20)

        # Generated passwords widget
        self.label_result = QLabel()
        layout.addWidget(self.label_result)

        self.input = QLineEdit()
        self.input.setReadOnly(True)
        layout.addWidget(self.input)

        # Check status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)

        # Checkbox for bypass
        self.bypass = QCheckBox()
        layout.addWidget(self.bypass)

        # Buttons
        buttons = QHBoxLayout()
        self.generate = QPushButton()
        self.copy = QPushButton()
        self.vault = QPushButton()

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

    def retranslate_ui(self):
        """Update all texts on tab"""
        # Checkboxes
        self.label_length.setText(translate.get_translation("gen_length"))
        self.cb_upper.setText(translate.get_translation("gen_upper"))
        self.cb_lower.setText(translate.get_translation("gen_lower"))
        self.cb_digits.setText(translate.get_translation("gen_digits"))
        self.cb_special.setText(translate.get_translation("gen_special"))
        self.bypass.setText(translate.get_translation("gen_bypass"))

        # Labels
        self.label_result.setText(translate.get_translation("gen_result_label"))
        self.input.setPlaceholderText(translate.get_translation("gen_placeholder"))

        # Buttons
        self.generate.setText(translate.get_translation("gen_btn_generate"))
        self.copy.setText(translate.get_translation("gen_btn_copy"))
        self.vault.setText(translate.get_translation("gen_btn_use"))

    def generation_handler(self):
        """Generate password"""

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

        self.status_label.setText(translate.get_translation("status_checking"))
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
                        translate.get_translation("status_init_db")
                    )
                    QApplication.processEvents()
                    self.ru_db.initialize()
                if self.ru_db.is_ready:
                    count = self.ru_db.check_password(password)
                else:
                    self.status_label.setText(
                        translate.get_translation("status_db_error")
                    )
                    self.status_label.setStyleSheet("color: #ff4d4d")
                    return
            else:
                # HIBP API
                api_name = "HIBP API"
                count = self.hibp_api.check_password_breach(password)

            if count == -1:  # Error
                msg = translate.get_translation("status_conn_error").format(
                    api=api_name
                )
                self.status_label.setText(msg)
                self.status_label.setStyleSheet("color: #ffa500")
            elif count > 0:  # No error, but still not good
                msg = translate.get_translation("status_found").format(
                    count=count, api=api_name
                )
                self.status_label.setText(msg)
                self.status_label.setStyleSheet("color:#ff4d4d;")
            else:
                msg = translate.get_translation("status_secure").format(api=api_name)
                self.status_label.setText(msg)
                self.status_label.setStyleSheet("color: #2ecc71;")

        except Exception as e:
            msg = translate.get_translation("status_error").format(error=str(e))
            self.status_label.setText(msg)

    def copy_to_clipboard(self):
        """Copy to clipboard"""
        if self.input.text():
            QApplication.clipboard().setText(self.input.text())
            QMessageBox.information(
                self,
                translate.get_translation("success_title"),
                translate.get_translation("gen_msg_copied"),
            )

    def on_use_in_vault(self):
        """Send password to main window for save in vault"""
        if self.input.text():
            self.password_used_in_vault.emit(self.input.text())
        else:
            QMessageBox.warning(
                self,
                translate.get_translation("warning_title"),
                translate.get_translation("gen_msg_gen_first"),
            )
