import json
import os

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

from gui_v2.config import AppConfig, SecurityConfig


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
        self.save = QPushButton("Save configuration")
        self.save.setMinimumHeight(40)
        self.save.setStyleSheet(
            "background-color: #4da3df; color: white; font-weight: bold;"
        )
        self.save.clicked.connect(self.save_settings)

        self.reset = QPushButton("Reset to defaults")
        self.reset.setMinimumHeight(40)
        self.reset.setStyleSheet("background-color: #555; color: white;")
        self.reset.clicked.connect(self.reset_settings)

        # Add save and reset buttons in layout
        buttons_layout.addWidget(self.save, 2)
        buttons_layout.addWidget(self.reset, 1)

        # Add widgets in main widget layout
        self.widget_layout.addStretch()
        self.widget_layout.addLayout(buttons_layout)

    def _setup_ui_groups(self):
        "Setting up ui groups"

        # AppConfig group
        app_config = QGroupBox("Application settings")
        app_form = QFormLayout()
        self.app_name = QLineEdit(AppConfig.APP_NAME)
        self.app_name.setReadOnly(True)
        self.version = QLineEdit(AppConfig.VERSION)
        self.version.setReadOnly(True)
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["English", "Русский"])
        app_form.addRow("App name:", self.app_name)
        app_form.addRow("Version:", self.version)
        app_form.addRow("Language:", self.lang_selector)
        app_config.setLayout(app_form)
        self.widget_layout.addWidget(app_config)

        # API's group
        api_config = QGroupBox("API / HIBP configuration")
        api_form = QFormLayout()
        self.delay = QDoubleSpinBox()
        self.delay.setRange(0.1, 10.0)
        self.delay.setValue(AppConfig.HIBP_REQUEST_DELAY)
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)
        self.timeout.setValue(AppConfig.HIBP_TIMEOUT)
        api_form.addRow("HIBP API request delay (sec):", self.delay)
        api_form.addRow("HIBP timeout (sec):", self.timeout)
        api_config.setLayout(api_form)
        self.widget_layout.addWidget(api_config)

        # SecurityConfig group
        security_config = QGroupBox("Security Configuration")
        security_form = QFormLayout()
        self.iter = QSpinBox()
        self.iter.setRange(1000, 9999999)
        self.iter.setValue(SecurityConfig.PBKDF2_ITERATIONS)
        self.rounds = QSpinBox()
        self.rounds.setRange(1, 31)
        self.rounds.setValue(SecurityConfig.BCRYPT_ROUNDS)
        self.salt_size = QSpinBox()
        self.salt_size.setRange(8, 128)
        self.salt_size.setValue(SecurityConfig.SALT_SIZE)
        self.lockout = QSpinBox()
        self.lockout.setRange(0, 86400)
        self.lockout.setValue(SecurityConfig.LOCKOUT_DURATION)
        security_form.addRow("PBKDF2 iterations:", self.iter)
        security_form.addRow("Bcrypt rounds:", self.rounds)
        security_form.addRow("Salt size (bytes):", self.salt_size)
        security_form.addRow("Lockout duration (sec):", self.lockout)
        security_config.setLayout(security_form)
        self.widget_layout.addWidget(security_config)

    def save_settings(self):
        "Save settings in file"
        try:
            # Update values
            AppConfig.HIBP_REQUEST_DELAY = self.delay.value()
            AppConfig.HIBP_TIMEOUT = self.timeout.value()
            AppConfig.LANGUAGE = self.lang_selector.currentText()
            SecurityConfig.PBKDF2_ITERATIONS = self.iter.value()
            SecurityConfig.BCRYPT_ROUNDS = self.rounds.value()
            SecurityConfig.SALT_SIZE = self.salt_size.value()
            SecurityConfig.LOCKOUT_DURATION = self.lockout.value()

            config_data = {
                "AppConfig": {
                    "HIBP_REQUEST_DELAY": AppConfig.HIBP_REQUEST_DELAY,
                    "HIBP_TIMEOUT": AppConfig.HIBP_TIMEOUT,
                    "LANGUAGE": AppConfig.LANGUAGE,
                },
                "SecurityConfig": {
                    "PBKDF2_ITERATIONS": SecurityConfig.PBKDF2_ITERATIONS,
                    "BCRYPT_ROUNDS": SecurityConfig.BCRYPT_ROUNDS,
                    "SALT_SIZE": SecurityConfig.SALT_SIZE,
                    "LOCKOUT_DURATION": SecurityConfig.LOCKOUT_DURATION,
                },
            }

            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)

            QMessageBox.information(self, "Success", "Configuration saved!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save failed: {e}")

    def reset_settings(self):
        "Reset settings"
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\nThis will delete your saved configuration file.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Delete settings file (if it exist)
            if os.path.exists("settings.json"):
                os.remove("settings.json")

            # Setting up defaults
            self.delay.setValue(1.6)
            self.timeout.setValue(10)
            self.lang_selector.setCurrentText("English")
            self.iter.setValue(100000)
            self.rounds.setValue(14)
            self.salt_size.setValue(32)
            self.lockout.setValue(900)

            AppConfig.HIBP_REQUEST_DELAY = 1.6
            AppConfig.HIBP_TIMEOUT = 10
            AppConfig.LANGUAGE = "English"
            SecurityConfig.PBKDF2_ITERATIONS = 100000
            SecurityConfig.BCRYPT_ROUNDS = 14
            SecurityConfig.SALT_SIZE = 32
            SecurityConfig.LOCKOUT_DURATION = 900

            # Info message
            QMessageBox.information(
                self,
                "Reset complete",
                "All settings have been restored to factory defaults.",
            )
