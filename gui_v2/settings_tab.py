from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QScrollArea,
    QComboBox,
)

from config import AppConfig, SecurityConfig


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()

        # Default layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Scroll area (if not all settings will fit)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Invisible scroll area frame
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        # Scroll widget
        widget = QWidget()
        self.widget_layout = QVBoxLayout(widget)
        self.widget_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.widget_layout.setSpacing(20)

        scroll.setWidget(widget)
        layout.addWidget(scroll)

        # App settings group
        app_config = QGroupBox("Application settings")
        app_form = QFormLayout()

        # App name (r mode)
        self.app_name = QLineEdit(AppConfig.APP_NAME)
        self.app_name.setReadOnly(True)
        self.app_name.setStyleSheet("color: #888;")
        app_form.addRow("App name:", self.app_name)

        # Version (r mode)
        self.version = QLineEdit(AppConfig.VERSION)
        self.version.setReadOnly(True)
        self.version.setStyleSheet("color: #888;")
        app_form.addRow("Version:", self.version)

        # Language selector (rw mode)
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["English", "Русский"])
        app_form.addRow("Language:", self.lang_selector)

        # Add to layout
        app_config.setLayout(app_form)
        self.widget_layout.addWidget(app_config)

        # HIBP settings group
        api_config = QGroupBox("API / HIBP configuration")
        api_form = QFormLayout()

        # HIBP Delay (rw mode)
        self.delay = QDoubleSpinBox()
        self.delay.setRange(0.1, 10.0)
        self.delay.setSingleStep(0.1)
        self.delay.setValue(AppConfig.HIBP_REQUEST_DELAY)
        api_form.addRow("HIBP API request delay (sec):", self.delay)

        # HIBP Timeout (rw mode)
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 60)
        self.timeout.setValue(AppConfig.HIBP_TIMEOUT)
        api_form.addRow("HIBP timeout (sec):", self.timeout)

        # Add to layout
        api_config.setLayout(api_form)
        self.widget_layout.addWidget(api_config)

        # Security settings group
        security_config = QGroupBox("Security Configuration")
        security_form = QFormLayout()

        # PBKDF2 terations
        self.iter = QSpinBox()
        self.iter.setRange(1000, 9999999)
        self.iter.setSingleStep(1000)
        self.iter.setValue(SecurityConfig.PBKDF2_ITERATIONS)
        security_form.addRow("PBKDF2 iterations:", self.iter)

        # Bcrypt rounds
        self.rounds = QSpinBox()
        self.rounds.setRange(1, 31)
        self.rounds.setValue(SecurityConfig.BCRYPT_ROUNDS)
        security_form.addRow("Bcrypt rounds:", self.rounds)

        # Salt size
        self.salt_size = QSpinBox()
        self.salt_size.setRange(8, 128)
        self.salt_size.setValue(SecurityConfig.SALT_SIZE)
        security_form.addRow("Salt size (bytes):", self.salt_size)

        # Lockout duration
        self.lockout = QSpinBox()
        self.lockout.setRange(0, 86400)
        self.lockout.setValue(SecurityConfig.LOCKOUT_DURATION)
        security_form.addRow("Lockout duration (sec):", self.lockout)

        # Add to layout
        security_config.setLayout(security_form)
        self.widget_layout.addWidget(security_config)

        # Buttons
        self.save = QPushButton("Save configuration")
        self.save.setMinimumHeight(40)

        ######### Placeholder #########
        self.save.clicked.connect(self.save_settings)

        # Add to layout
        self.widget_layout.addStretch()
        self.widget_layout.addWidget(self.save)

    def save_settings(self):
        "Placeholder"
        print("Configuration saved")
