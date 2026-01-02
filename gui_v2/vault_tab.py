from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QCheckBox,
    QTextEdit,
    QFrame,
)


class VaultTab(QWidget):
    "Vault tab"

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Services list (Left side)
        left = QVBoxLayout()
        self.stored_services_label = QLabel("Stored services:")
        self.services_list = QListWidget()

        left.addWidget(self.stored_services_label)
        left.addWidget(self.services_list)

        # Form (Right side)
        right = QFrame()
        right_layout = QVBoxLayout(right)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Form's fields
        self.service_input = QLineEdit()
        self.name_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_pass = QCheckBox("Show password")

        self.show_pass.stateChanged.connect(self.toggle_password_visibility)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Some notes...")

        # Field's grid
        grid = QGridLayout()
        grid.addWidget(QLabel("Service:"), 0, 0)
        grid.addWidget(self.service_input, 0, 1)
        grid.addWidget(QLabel("Username:"), 1, 0)
        grid.addWidget(self.name_input, 1, 1)
        grid.addWidget(QLabel("Password:"), 2, 0)
        grid.addWidget(self.pass_input, 2, 1)
        grid.addWidget(QLabel(""), 3, 0)
        grid.addWidget(self.show_pass, 3, 1)
        grid.addWidget(QLabel("Notes:"), 4, 0)
        grid.addWidget(self.notes_input, 4, 1)

        right_layout.addLayout(grid)

        # Buttons
        buttons = QHBoxLayout()
        self.save_button = QPushButton("Save entry")
        self.clear_button = QPushButton("Clear entry")
        self.delete_button = QPushButton("Delete entry")
        self.refresh_button = QPushButton("Refresh")

        buttons.addWidget(self.save_button)
        buttons.addWidget(self.clear_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.refresh_button)

        right_layout.addSpacing(20)
        right_layout.addLayout(buttons)
        right_layout.addStretch()

        layout.addLayout(left, 1)
        layout.addWidget(right, 2)

        # Logic connection
        self.services_list.itemClicked.connect(self.load_entry)

    def toggle_password_visibility(self):
        if self.show_pass.isChecked():
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

    def load_entry(self, item):
        #####################################################
        ## The functions from vault will be connected here ##
        #####################################################

        print(f"Loading data for: {item.text()}")
        self.service_input.setText(item.text())
