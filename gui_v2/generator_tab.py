from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QSpinBox,
)


class GeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        # Default layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Grid generation
        grid = QGridLayout()

        # Spinbox
        self.spin = QSpinBox()
        self.spin.setRange(4, 128)
        self.spin.setValue(16)

        # Checkboxes
        self.cb_upper = QCheckBox("Uppercase letters (A-Z)")
        self.cb_upper.setChecked(True)
        self.cb_lower = QCheckBox("Lowercase letters (a-z)")
        self.cb_lower.setChecked(True)
        self.cb_digits = QCheckBox("Digits (0-9)")
        self.cb_digits.setChecked(True)
        self.cb_special = QCheckBox("Special characters (!@#$%)")
        self.cb_special.setChecked(True)

        # Grid settings
        grid.addWidget(QLabel("Password lenght:"), 0, 0)
        grid.addWidget(self.spin, 0, 1)
        grid.addWidget(self.cb_upper, 1, 0)
        grid.addWidget(self.cb_lower, 2, 0)
        grid.addWidget(self.cb_digits, 3, 0)
        grid.addWidget(self.cb_special, 4, 0)

        # Add grid to default layout
        layout.addLayout(grid)
        layout.addSpacing(20)

        # Generated passwords widget
        layout.addWidget(QLabel("Generated password:"))
        self.input = QLineEdit()
        self.input.setReadOnly(True)
        self.input.setStyleSheet("font-size: 16px; font-weight: bold; color: #4da3df;")
        layout.addWidget(self.input)

        # Checkbox for bypass
        self.bypass = QCheckBox("Use Russian bypass")
        layout.addWidget(self.bypass)

        # Buttons
        buttons = QHBoxLayout()
        self.generate = QPushButton("Generate password")
        self.copy = QPushButton("Copy to clipboard")
        self.vault = QPushButton("Use in vault")

        # Buttons layout
        buttons.addWidget(self.generate)
        buttons.addWidget(self.copy)
        buttons.addWidget(self.vault)

        # Add buttons to default layout
        layout.addLayout(buttons)
        layout.addStretch()

        ##################################################################
        ## The functions from pass_gen and vault will be connected here ##
        ##################################################################
        # self.generate.clicked.connect(self...)
