from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from gui.translator import translate
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
        # Default layout (vertical)
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
        checkboxes.setSpacing(10)

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
        layout.addLayout(checkboxes)

        # Button layout (horizontal)
        button_layout = QHBoxLayout()
        self.check = QPushButton()
        self.check.setFixedHeight(40)
        self.check.setMinimumWidth(200)

        # Connect check handler
        self.check.clicked.connect(self.check_handler)

        button_layout.addWidget(self.check)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Process status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(self.status_label)
        layout.addSpacing(20)

        # Trust block (Filler), vertical layout
        trust_layout = QVBoxLayout()
        trust_layout.setSpacing(5)

        # Trust title
        self.trust_title = QLabel()
        self.trust_title.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #a0a0a0;"
        )

        # Trust description
        self.trust_desc = QLabel()
        self.trust_desc.setWordWrap(True)
        self.trust_desc.setStyleSheet("color: #888888; font-size: 12px;")

        trust_layout.addWidget(self.trust_title)
        trust_layout.addWidget(self.trust_desc)
        layout.addLayout(trust_layout)
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
        self.trust_title.setText(translate.get_translation("trust_title"))
        self.trust_desc.setText(translate.get_translation("trust_desc"))

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
