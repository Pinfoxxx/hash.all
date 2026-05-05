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
    QFrame,
    QProgressBar,
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
        layout.addSpacing(20) # Add upper space

        # Label
        self.header_label = QLabel()
        layout.addWidget(self.header_label)

        # Input layout (vertical)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(2)

        # Password entry line
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.input.textChanged.connect(self.update_strength_indicator) # Strength indicator
        layout.addWidget(self.input)

        # Strength indicator
        self.strength_bar = QProgressBar()
        self.strength_bar.setFixedHeight(4)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setStyleSheet("""
            QProgressBar { border: none; background-color: #333333; border-radius: 2px; }
            QProgressBar::chunk { background-color: transparent; border-radius: 2px; }
        """)
        input_layout.addWidget(self.strength_bar)
        layout.addLayout(input_layout)

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

        # Alert box
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        self.status_label.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(self.status_label)
        layout.addSpacing(10)

        # Trust block frame
        self.trust_frame = QFrame()
        # self.trust_frame.setMaximumWidth(650)
        self.trust_frame.setStyleSheet("""
                    QFrame {
                        background-color: #242424; 
                        border: 1px solid #363636; 
                        border-radius: 8px;
                    }
                    QLabel {
                        border: none;
                        background: transparent;
                    }
                """)
        # Trust block layout
        trust_layout = QVBoxLayout(self.trust_frame)
        trust_layout.setSpacing(5)
        trust_layout.setContentsMargins(15, 15, 15, 15)

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
        layout.addWidget(self.trust_frame)

        # Trust block wrapper
        # trust_wrapper = QHBoxLayout()
        # trust_wrapper.addWidget(self.trust_frame)
        # trust_wrapper.addStretch()
        # layout.addLayout(trust_wrapper)

        layout.addStretch()

    def update_strength_indicator(self, text):
        """Strength logic for progress bar"""
        length = len(text)
        if length == 0:
            self.strength_bar.setValue(0)
            color = "transparent"
        elif length < 6:
            self.strength_bar.setValue(33)
            color = "#ff4d4d" # Red (weak)
        elif length < 10:
            self.strength_bar.setValue(66)
            color = "#ffa500" # Yellow (medium)
        else:
            self.strength_bar.setValue(100)
            color = "#2ecc71" # Green (safe ... maybe idk)

        self.strength_bar.setStyleSheet(f"""
                    QProgressBar {{ border: none; background-color: #333333; border-radius: 2px; }}
                    QProgressBar::chunk {{ background-color: {color}; border-radius: 2px; }}
                """)

    def set_status_style(self, style_type):
        """Applying QSS style to bar"""
        base_style = "font-weight: bold; font-size: 13px; border-radius: 6px;"

        if style_type == "checking":
            # Blue bar (checking)
            self.status_label.setStyleSheet(
                base_style + "color: #4da3df; background-color: #172A3A; border: 1px solid #234D6E;")
        elif style_type == "found":
            # Red bar (bad)
            self.status_label.setStyleSheet(
                base_style + "color: #ff4d4d; background-color: #3A1717; border: 1px solid #6E2323;")
        elif style_type == "secure":
            # Green bar (good)
            self.status_label.setStyleSheet(
                base_style + "color: #2ecc71; background-color: #173A21; border: 1px solid #236E39;")
        elif style_type == "error":
            # Orange bar (connection error)
            self.status_label.setStyleSheet(
                base_style + "color: #ffa500; background-color: #3A2B17; border: 1px solid #6E5323;")

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
        self.set_status_style("checking")
        self.status_label.setVisible(True)
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
                    self.set_status_style("error")
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
                self.set_status_style("error")
            elif count > 0:  # No error, but still not good
                msg = translate.get_translation("status_found").format(
                    count=count, api=api_name
                )
                self.status_label.setText(msg)
                self.set_status_style("found")
            else:
                msg = translate.get_translation("status_secure").format(api=api_name)
                self.status_label.setText(msg)
                self.set_status_style("secure")

        except Exception as e:
            msg = translate.get_translation("status_error").format(error=str(e))
            self.status_label.setText(msg)
            self.set_status_style("error")

        finally:
            self.check.setEnabled(True)
