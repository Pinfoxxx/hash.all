from config import cfg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsTab(QWidget):
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

        # Setting up ui groups
        self._setup_ui_groups()

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Buttons
        self.save_btn = QPushButton("Save configuration")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet(
            "background-color: #4da3df; color: white; font-weight: bold;"
        )
        self.save_btn.clicked.connect(self.save_settings)

        self.reset_btn = QPushButton("Reset to defaults")
        self.reset_btn.setMinimumHeight(40)
        self.reset_btn.setStyleSheet("background-color: #555; color: white;")
        self.reset_btn.clicked.connect(self.reset_settings)

        # Add save and reset buttons in layout
        buttons_layout.addWidget(self.save_btn, 2)
        buttons_layout.addWidget(self.reset_btn, 1)

        # Add widgets in main widget layout
        self.widget_layout.addStretch()
        self.widget_layout.addLayout(buttons_layout)

    def _setup_ui_groups(self):
        "Setting up ui groups"

        # Application settings
        app_config = QGroupBox("Application settings")
        app_form = QFormLayout()
        self.app_name = QLineEdit()
        self.app_name.setReadOnly(True)
        self.version = QLineEdit()
        self.version.setReadOnly(True)
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["English", "Русский"])

        # Add in widget layout
        app_form.addRow("App name:", self.app_name)
        app_form.addRow("Version:", self.version)
        app_form.addRow("Language:", self.lang_selector)
        app_config.setLayout(app_form)
        self.widget_layout.addWidget(app_config)

        # API settings
        api_config = QGroupBox("API / HIBP configuration")
        api_form = QFormLayout()
        self.delay = QDoubleSpinBox()
        self.delay.setRange(0.1, 10.0)
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)

        # Add in widget layout
        api_form.addRow("HIBP API request delay (sec):", self.delay)
        api_form.addRow("HIBP timeout (sec):", self.timeout)
        api_config.setLayout(api_form)
        self.widget_layout.addWidget(api_config)

        # Security settings
        security_config = QGroupBox("Security Configuration")
        security_form = QFormLayout()
        self.iter = QSpinBox()
        self.iter.setRange(1000, 9999999)
        self.rounds = QSpinBox()
        self.rounds.setRange(1, 31)
        self.salt_size = QSpinBox()
        self.salt_size.setRange(8, 128)
        self.lockout = QSpinBox()
        self.lockout.setRange(0, 86400)

        # Add in widget layout
        security_form.addRow("PBKDF2 iterations:", self.iter)
        security_form.addRow("Bcrypt rounds:", self.rounds)
        security_form.addRow("Salt size (bytes):", self.salt_size)
        security_form.addRow("Lockout duration (sec):", self.lockout)
        security_config.setLayout(security_form)
        self.widget_layout.addWidget(security_config)

    def _load_values(self):
        "Fill widgets with data from cfg.data"
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

    def save_settings(self):
        """Read data from UI and save in file"""
        cfg.data.LANGUAGE = self.lang_selector.currentText()
        cfg.data.HIBP_REQUEST_DELAY = self.delay.value()
        cfg.data.HIBP_TIMEOUT = self.timeout.value()
        cfg.data.PBKDF2_ITERATIONS = self.iter.value()
        cfg.data.BCRYPT_ROUNDS = self.rounds.value()
        cfg.data.SALT_SIZE = self.salt_size.value()
        cfg.data.LOCKOUT_DURATION = self.lockout.value()

        # Save config
        cfg.save()
        QMessageBox.information(self, "Success", "Configuration saved sucessfully!")

    def reset_settings(self):
        """Resetting the settings and loading them into the UI"""
        reply = QMessageBox.question(
            self,
            "Confirm reset",
            "Are you sure want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            cfg.reset()
            self._load_values()
            QMessageBox.information(self, "Reset", "Settings have been reset.")
