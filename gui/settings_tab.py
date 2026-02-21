from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gui_v2.config import cfg
from gui_v2.translator import translate


class SettingsTab(QWidget):
    """Settings tab widget"""

    languageChanged = Signal()

    def __init__(self):
        super().__init__()

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Setup scroll area (if it need)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        # Setup widgets layout
        widget = QWidget()
        self.widget_layout = QVBoxLayout(widget)
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.widget_layout.setSpacing(20)

        # Add scroll in layout
        scroll.setWidget(widget)
        layout.addWidget(scroll)

        # Create widgets without text
        self._setup_ui_elements()

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Buttons
        self.save_btn = QPushButton()
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet(
            "background-color: #4da3df; color: white; font-weight: bold;"
        )
        self.save_btn.clicked.connect(self.save_settings)

        self.reset_btn = QPushButton()
        self.reset_btn.setMinimumHeight(40)
        self.reset_btn.setStyleSheet("background-color: #555; color: white;")
        self.reset_btn.clicked.connect(self.reset_settings)

        # Add save and reset buttons in layout
        buttons_layout.addWidget(self.save_btn, 2)
        buttons_layout.addWidget(self.reset_btn, 1)

        # Add widgets in main widget layout
        self.widget_layout.addStretch()
        self.widget_layout.addLayout(buttons_layout)

        # Apply translate
        self.retranslate_ui()

        # Initial loading
        self._load_values()

    def _setup_ui_elements(self):
        """Setting up ui groups"""

        # Application settings
        self.app_config = QGroupBox()
        app_form = QFormLayout()
        self.app_name = QLineEdit()
        self.app_name.setReadOnly(True)
        self.version = QLineEdit()
        self.version.setReadOnly(True)
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["English", "Русский"])

        # Create links to labels for text switching
        self.label_app_name = QLabel()
        self.label_version = QLabel()
        self.label_lang = QLabel()

        # Add in widget layout
        app_form.addRow(self.label_app_name, self.app_name)
        app_form.addRow(self.label_version, self.version)
        app_form.addRow(self.label_lang, self.lang_selector)
        self.app_config.setLayout(app_form)
        self.widget_layout.addWidget(self.app_config)

        # API settings
        self.api_config = QGroupBox()
        api_form = QFormLayout()

        self.label_delay = QLabel()
        self.label_timeout = QLabel()

        self.delay = QDoubleSpinBox()
        self.delay.setRange(0.1, 10.0)
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)

        # Add in widget layout
        api_form.addRow(self.label_delay, self.delay)
        api_form.addRow(self.label_timeout, self.timeout)
        self.api_config.setLayout(api_form)
        self.widget_layout.addWidget(self.api_config)

        # Security settings
        self.security_config = QGroupBox()
        security_form = QFormLayout()
        self.label_security_warning = QLabel()
        self.label_security_warning.setWordWrap(True)
        self.label_security_warning.setStyleSheet("color: #e74c3c; margin-bottom: 5px;")
        self.iter = QSpinBox()
        self.iter.setRange(1000, 9999999)
        self.rounds = QSpinBox()
        self.rounds.setRange(1, 31)
        self.salt_size = QSpinBox()
        self.salt_size.setRange(8, 128)
        self.lockout = QSpinBox()
        self.lockout.setRange(0, 86400)

        self.label_iter = QLabel()
        self.label_rounds = QLabel()
        self.label_salt = QLabel()
        self.label_lockout = QLabel()

        # Add in widget layout
        security_form.addRow(self.label_iter, self.iter)
        security_form.addRow(self.label_rounds, self.rounds)
        security_form.addRow(self.label_salt, self.salt_size)
        security_form.addRow(self.label_lockout, self.lockout)
        security_form.addRow(self.label_security_warning)
        self.security_config.setLayout(security_form)
        self.widget_layout.addWidget(self.security_config)

    def retranslate_ui(self):
        """Update all texts in ui"""
        # Group's titles
        self.app_config.setTitle(translate.get_translation("app_settings"))
        self.api_config.setTitle(translate.get_translation("api_settings"))
        self.security_config.setTitle(translate.get_translation("security_settings"))

        # Form's labels
        self.label_app_name.setText(translate.get_translation("app_name"))
        self.label_version.setText((translate.get_translation("version")))
        self.label_lang.setText(translate.get_translation("language"))
        self.label_delay.setText(translate.get_translation("hibp_api_delay"))
        self.label_timeout.setText(translate.get_translation("hibp_timeout"))
        self.label_iter.setText(translate.get_translation("pbkdf2_iterations"))
        self.label_rounds.setText(translate.get_translation("bcrypt_rounds"))
        self.label_salt.setText(translate.get_translation("salt_size"))
        self.label_lockout.setText(translate.get_translation("lockout"))
        self.label_security_warning.setText(
            translate.get_translation("security_warning")
        )

        # Buttons texts
        self.save_btn.setText(translate.get_translation("save_btn"))
        self.reset_btn.setText(translate.get_translation("reset_btn"))

    def _load_values(self):
        """Fill widgets with data from cfg.data"""
        d = cfg.data

        # Set defaults from cfg
        self.app_name.setText(d.APP_NAME)
        self.version.setText(d.VERSION)
        self.lang_selector.setCurrentText(d.LANGUAGE)
        self.delay.setValue(d.HIBP_REQUEST_DELAY)
        self.timeout.setValue(d.HIBP_TIMEOUT)
        self.iter.setValue(d.PBKDF2_ITERATIONS)
        self.rounds.setValue(d.BCRYPT_ROUNDS)
        self.salt_size.setValue(d.SALT_SIZE)
        self.lockout.setValue(d.LOCKOUT_DURATION)

    def refresh_values(self):
        """Public method to force refresh UI from config object"""
        self._load_values()

    def save_settings(self):
        """Read data from UI and save in file"""
        old_lang = cfg.data.LANGUAGE
        new_lang = self.lang_selector.currentText()

        cfg.data.LANGUAGE = new_lang
        cfg.data.HIBP_REQUEST_DELAY = self.delay.value()
        cfg.data.HIBP_TIMEOUT = self.timeout.value()
        cfg.data.PBKDF2_ITERATIONS = self.iter.value()
        cfg.data.BCRYPT_ROUNDS = self.rounds.value()
        cfg.data.SALT_SIZE = self.salt_size.value()
        cfg.data.LOCKOUT_DURATION = self.lockout.value()

        # Save config
        cfg.save()

        if old_lang != new_lang:
            translate.load_language()
            self.retranslate_ui()
            self.languageChanged.emit()

            QMessageBox.information(
                self,
                translate.get_translation("success_title"),
                translate.get_translation("language_changed_msg"),
            )
        else:
            QMessageBox.information(
                self,
                translate.get_translation("success_title"),
                translate.get_translation("success_msg"),
            )

    def reset_settings(self):
        """Resetting the settings and loading them into the UI"""
        reply = QMessageBox.question(
            self,
            translate.get_translation("confirm_reset_title"),
            translate.get_translation("confirm_reset_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            cfg.reset()
            self._load_values()
            translate.load_language()
            self.retranslate_ui()
            self.languageChanged.emit()

        QMessageBox.information(
            self,
            translate.get_translation("reset_success_title"),
            translate.get_translation("reset_success_msg"),
        )
