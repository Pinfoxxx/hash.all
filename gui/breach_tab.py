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

from gui_v2.translator import translate
from web_requests.hibp_api import HIBPClient
from web_requests.russian_api.hash_search import HashDBSearch


class CheckTab(QWidget):
    """Check tab widget"""

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

        # Label
        self.header_label = QLabel()
        layout.addWidget(self.header_label)

        # Password entry line
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input)

        # Checkboxes layout
        checkboxes = QVBoxLayout()

        # Checkboxes
        self.cb_show = QCheckBox()
        self.cb_show.stateChanged.connect(
            lambda: self.input.setEchoMode(
                QLineEdit.EchoMode.Normal
                if self.cb_show.isChecked()
                else QLineEdit.EchoMode.Password
            )
        )
        self.cb_bypass = QCheckBox()

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
        self.check = QPushButton()
        self.check.setFixedHeight(40)

        # Connect check handler
        self.check.clicked.connect(self.check_handler)

        # Add widgets in layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.check)
        layout.addStretch()

    def retranslate_ui(self):
        """Update all texts in ui"""
        self.header_label.setText(translate.get_translation("check_header"))
        self.input.setPlaceholderText(
            translate.get_translation("enter_pass_placeholder")
        )
        self.cb_show.setText(translate.get_translation("show_pass"))
        self.cb_bypass.setText(translate.get_translation("use_ru_db"))
        self.check.setText(translate.get_translation("check_btn"))

    def check_handler(self):
        """Check password"""
        password = self.input.text()

        if not password:
            QMessageBox.warning(
                self,
                translate.get_translation("warning_title"),
                translate.get_translation("empty_pass_msg"),
            )
            return

        # Indication
        self.status_label.setText(translate.get_translation("status_checking"))
        self.status_label.setStyleSheet("color: #4da3df;")
        self.check.setEnabled(False)

        # Update UI
        QApplication.processEvents()

        count = 0
        api_name = ""

        try:
            if self.cb_bypass.isChecked():
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
                    self.status_label.setText("status_db_error")
                    self.status_label.setStyleSheet("color: #ff4d4d")
                    self.check.setEnabled(True)
                    return
            else:
                # HIBP db
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
                self.status_label.setStyleSheet("color: #ff4d4d")
            else:
                msg = translate.get_translation("status_secure").format(api=api_name)
                self.status_label.setText(msg)
                self.status_label.setStyleSheet("color: #2ecc71;")

        except Exception as e:
            msg = translate.get_translation("status_error").format(error=str(e))
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("color: #888;")

        finally:
            self.check.setEnabled(True)
