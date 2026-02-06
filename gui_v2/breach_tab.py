from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from web_requests.hibp_api import HIBPClient
from web_requests.russian_api.hash_search import HashDBSearch


class CheckTab(QWidget):
    def __init__(self):
        super().__init__()

        # Initializing API
        self.hibp_api = HIBPClient()
        # Russian database (debug-only)
        self.ru_db = HashDBSearch("https://disk.yandex.ru/d/O22Pp0Anlf0rRA")
        # Initializing gui
        self.init_ui()

    def init_ui(self):
        # Default layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Label
        layout.addWidget(QLabel("Check password security:"))

        # Password entry line
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter password to check...")
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input)

        # Checkboxes layout
        checkboxes = QVBoxLayout()
        self.cb_show = QCheckBox("Show password")
        self.cb_show.stateChanged.connect(
            lambda: self.input.setEchoMode(
                QLineEdit.EchoMode.Normal
                if self.cb_show.isChecked()
                else QLineEdit.EchoMode.Password
            )
        )
        self.cb_bypass = QCheckBox("Use Russian bypass")

        # Add checkboxes to layout
        checkboxes.addWidget(self.cb_show)
        checkboxes.addWidget(self.cb_bypass)
        checkboxes.addStretch()
        layout.addLayout(checkboxes)

        # Process status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-weight: bold; font-size: 13px;")

        # Buttons
        self.check = QPushButton("Check password")
        self.check.setFixedHeight(40)

        # Connect check handler
        self.check.clicked.connect(self.check_handler)

        # Add widgets in layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.check)
        layout.addStretch()

    def check_handler(self):
        "Check password"
        password = self.input.text()

        if not password:
            QMessageBox.warning(self, "Warning", "Please enter a password to check.")
            return

        # Indication
        self.status_label.setText("🔍 Checking database, please wait...")
        self.status_label.setStyleSheet("color: #4da3df;")
        self.check.setEnabled(False)

        # Update UI
        QApplication.processEvents()

        count = 0
        api_name = ""

        try:
            if self.cb_bypass.isChecked():
                api_name = "Russian DB"
                if self.ru_db.is_ready:
                    count = self.ru_db.check_password(password)
                else:
                    self.status_label.setText("❌  Russian DB is not initialized")
                    self.status_label.setStyleSheet("color: #ff4d4d")
                    self.check.setEnabled(True)
                    return
            else:
                # HIBP db
                api_name = "HIBP API"
                count = self.hibp_api.check_password_breach(password)

            if count == -1:  # Error
                self.status_label.setText(f"⚠️ Connection error with {api_name}")
                self.status_label.setStyleSheet("color: #ffa500")
            elif count > 0:  # No error, but still not good
                self.status_label.setText(
                    f"❌  Found in {count} breaches ({api_name})!"
                )
                self.status_label.setStyleSheet("color: #ff4d4d")
            else:
                self.status_label.setText(f"✅ Secure (Verified via {api_name})")
                self.status_label.setStyleSheet("color: #2ecc71;")

        except Exception as e:
            self.status_label.setText(f"⚠️ Error: {str(e)}")
            self.status_label.setStyleSheet("color: #888;")

        finally:
            self.check.setEnabled(True)
