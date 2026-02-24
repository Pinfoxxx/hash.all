from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.translator import translate
from web_requests.hibp_api import HIBPClient
from web_requests.russian_api.hash_search import HashDBSearch


class PasswordCheckThread(QThread):
    """Фоновый поток для проверки пароля без зависания GUI"""

    finished_signal = Signal(int, str)
    error_signal = Signal(str)
    init_db_signal = Signal()

    def __init__(self, password, use_bypass, hibp_api, ru_db):
        super().__init__()
        self.password = password
        self.use_bypass = use_bypass
        self.hibp_api = hibp_api
        self.ru_db = ru_db
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        try:
            count = 0
            api_name = ""

            if self.use_bypass:
                api_name = "Russian DB"
                if not self.ru_db.is_ready:
                    self.init_db_signal.emit()
                    self.ru_db.initialize()

                if self.is_cancelled:
                    return

                if self.ru_db.is_ready:
                    count = self.ru_db.check_password(self.password)
                else:
                    self.error_signal.emit("DB_ERROR")
                    return
            else:
                api_name = "HIBP API"
                if self.is_cancelled:
                    return
                count = self.hibp_api.check_password_breach(self.password)

            if self.is_cancelled:
                return

            self.finished_signal.emit(count, api_name)

        except Exception as e:
            if not self.is_cancelled:
                self.error_signal.emit(str(e))


class CheckTab(QWidget):
    """Check tab widget"""

    def __init__(self):
        super().__init__()

        # Initializing APIs
        self.hibp_api = HIBPClient()
        self.ru_db = HashDBSearch()

        # Initializing gui
        self.init_ui()

        # Link to the background thread
        self.check_thread = None

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

    def _show_msg_box(self, icon_type, title, text):
        """Method for render messageboxes without icons on "OK" button"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon_type)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)

        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)

        msg_box.exec()

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
            self._show_msg_box(
                QMessageBox.Icon.Warning,
                translate.get_translation("warning_title"),
                translate.get_translation("empty_pass_msg"),
            )
            return

        # Indication
        self.status_label.setText(translate.get_translation("status_checking"))
        self.status_label.setStyleSheet("color: #4da3df;")
        self.check.setEnabled(False)

        if self.check_thread is not None and self.check_thread.isRunning():
            self.check_thread.cancel()

        self.check_worker = PasswordCheckWorker(
            password=password,
            use_bypass=self.cb_bypass.isChecked(),
            hibp_api=self.hibp_api,
            ru_db=self.ru_db,
        )

        self.check_worker.init_db_signal.connect(self.on_check_init)
        self.check_worker.finished_signal.connect(self.on_check_finished)
        self.check_worker.error_signal.connect(self.on_check_error)

        self.check_worker.start()

    def on_check_init(self):
        """Update UI during DB init"""
        self.status_label.setText(translate.get_translation("status_init_db"))

    def on_check_finished(self, count, api_name):
        """Handling a successful response from API"""
        if count == -1:  # Error
            msg = translate.get_translation("status_conn_error").format(api=api_name)
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

        self.check.setEnabled(True)

    def on_check_error(self, error_msg):
        """Handling errors from thread"""
        if error_msg == "DB_ERROR":
            self.status_label.setText(translate.get_translation("status_db_error"))
            self.status_label.setStyleSheet("color: #ff4d4d")
        else:
            msg = translate.get_translation("status_error").format(error=error_msg)
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("color: #ff4d4d")

        self.check.setEnabled(True)
