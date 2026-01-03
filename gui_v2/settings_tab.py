from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QScrollArea,
)

from config import AppConfig


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

        # App config settings group
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
