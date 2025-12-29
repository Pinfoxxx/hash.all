from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QMessageBox,
)


class CheckTab(QWidget):
    def __init__(self):
        super().__init__()

        # Default layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Label
        layout.addWidget(QLabel("Check password security:"))

        # Password entry line
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter password to check...")
        self.input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input)

        # Checkboxes layout
        checkboxes = QVBoxLayout()
        self.show = QCheckBox("Show password")
        self.show.stateChanged.connect(
            lambda: self.input.setEchoMode(
                QLineEdit.Normal if self.show.isChecked() else QLineEdit.Password
            )
        )
