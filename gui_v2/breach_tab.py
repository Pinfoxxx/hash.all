from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
)


class CheckTab(QWidget):
    def __init__(self):
        super().__init__()

        # Default layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Label
        layout.addWidget(QLabel("Check password security:"))

        # Password entry line
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter password to check...")
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input)

        # Checkboxes layout
        checkboxes = QVBoxLayout()
        self.cb_show = QCheckBox("Show password")
        self.cb_show.stateChanged.connect(
            lambda: self.input.setEchoMode(
                QLineEdit.EchoMode.Normal
                if self.cb_show.isChecked()
                else QLineEdit.EchoMode.Password
            )
        )
        self.cb_bypass = QCheckBox("Use russian bypass")

        # Add checkboxes to layout
        checkboxes.addWidget(self.cb_show)
        checkboxes.addWidget(self.cb_bypass)
        checkboxes.addStretch()
        layout.addLayout(checkboxes)

        # Buttons
        self.check = QPushButton("Check password")

        ######################################################
        ### The functions from APIs will be connected here ###
        ######################################################

        # self.check.clicked.connect(self...)
        layout.addWidget(self.check)
        layout.addStretch()
