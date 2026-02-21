from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from keys.vault import VaultManager

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.translator import translate
from models.vault_model import VaultEntryModel


class VaultTab(QWidget):
    "Vault tab widget"

    def __init__(self):
        super().__init__()

        self.vault_manager: Optional["VaultManager"] = None

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Services list (Left side)
        left = QVBoxLayout()
        self.stored_services_label = QLabel()
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

        self.show_pass = QCheckBox()
        self.show_pass.stateChanged.connect(self.toggle_password_visibility)

        self.notes_input = QTextEdit()

        # Field's grid
        grid = QGridLayout()

        # Labels
        self.label_service = QLabel()
        self.label_username = QLabel()
        self.label_password = QLabel()
        self.label_notes = QLabel()

        # Add widgets to grid
        grid.addWidget(self.label_service, 0, 0)
        grid.addWidget(self.service_input, 0, 1)
        grid.addWidget(self.label_username, 1, 0)
        grid.addWidget(self.name_input, 1, 1)
        grid.addWidget(self.label_password, 2, 0)
        grid.addWidget(self.pass_input, 2, 1)
        grid.addWidget(QLabel(""), 3, 0)
        grid.addWidget(self.show_pass, 3, 1)
        grid.addWidget(self.label_notes, 4, 0)
        grid.addWidget(self.notes_input, 4, 1)

        right_layout.addLayout(grid)

        # Buttons
        buttons = QHBoxLayout()
        self.save_button = QPushButton()
        self.clear_button = QPushButton()
        self.delete_button = QPushButton()
        self.refresh_button = QPushButton()

        # Add widgets in layout
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

        # Buttons connection
        self.save_button.clicked.connect(self.save_entry)
        self.clear_button.clicked.connect(self.clear_form)
        self.delete_button.clicked.connect(self.delete_entry)
        self.refresh_button.clicked.connect(self.refresh_list)

        # Apply translate at start
        self.retranslate_ui()

    def retranslate_ui(self):
        """Update all texts on tab"""
        # Labels
        self.stored_services_label.setText(
            translate.get_translation("vault_stored_services")
        )
        self.label_service.setText(translate.get_translation("vault_service"))
        self.label_username.setText(translate.get_translation("vault_username"))
        self.label_password.setText(translate.get_translation("vault_password"))
        self.label_notes.setText(translate.get_translation("vault_notes"))

        # Checkboxes
        self.show_pass.setText(translate.get_translation("vault_show_pass"))

        # Placeholder text
        self.notes_input.setPlaceholderText(
            translate.get_translation("vault_notes_placeholder")
        )

        # Buttons
        self.save_button.setText(translate.get_translation("vault_btn_save"))
        self.clear_button.setText(translate.get_translation("vault_btn_clear"))
        self.delete_button.setText(translate.get_translation("vault_btn_delete"))
        self.refresh_button.setText(translate.get_translation("vault_btn_refresh"))

    def set_vault_manager(self, manager: "VaultManager"):
        """Dependency injection"""
        self.vault_manager = manager
        self.refresh_list()

    def toggle_password_visibility(self):
        if self.show_pass.isChecked():
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

    def clear_form(self):
        "Clear form fields"
        self.service_input.clear()
        self.name_input.clear()
        self.pass_input.clear()
        self.notes_input.clear()

    def refresh_list(self):
        "Refresh service list"
        if not self.vault_manager:
            return

        self.services_list.clear()
        try:
            services = self.vault_manager.list_services()
            self.services_list.addItems(services)
        except Exception as e:
            QMessageBox.critical(
                self,
                translate.get_translation("error_title"),
                translate.get_translation("vault_err_refresh").format(error=e),
            )

    def load_entry(self, item: QListWidgetItem):
        """Load service entry in form"""
        if not self.vault_manager:
            return

        service_name = item.text()
        print(f"Loading data for: {service_name}")  # Just for debugging

        entry = self.vault_manager.get_entry(service_name)

        if entry:
            self.service_input.setText(entry.service)
            self.name_input.setText(entry.username)
            self.pass_input.setText(entry.password)
            self.notes_input.setText(entry.notes)
        else:
            QMessageBox.warning(
                self,
                translate.get_translation("warning_title"),
                translate.get_translation("vault_warn_decrypt"),
            )

    def save_entry(self):
        """Collect data from UI, creating object and send it to the manager"""
        if not self.vault_manager:
            QMessageBox.critical(
                self,
                translate.get_translation("error_title"),
                translate.get_translation("vault_err_no_manager"),
            )
            return

        service = self.service_input.text().strip()
        username = self.name_input.text().strip()
        password = self.pass_input.text().strip()
        notes = self.notes_input.toPlainText()

        # Basic validation on UI level
        if not service or not username or not password:
            QMessageBox.warning(
                self,
                translate.get_translation("validation_error"),
                translate.get_translation("vault_warn_required"),
            )
            return

        try:
            # Creating pydantic model
            entry_model = VaultEntryModel(
                service=service, username=username, password=password, notes=notes
            )

            # Send model in logic layer
            if self.vault_manager.add_entry(entry_model):
                QMessageBox.information(
                    self,
                    translate.get_translation("success_title"),
                    translate.get_translation("vault_success_saved").format(
                        service=service
                    ),
                )
                self.refresh_list()
                self.clear_form()
            else:
                QMessageBox.warning(
                    self,
                    translate.get_translation("error_title"),
                    translate.get_translation("vault_err_save"),
                )

        except ValueError as ve:
            # Validation errors
            QMessageBox.warning(
                self, translate.get_translation("validation_error"), str(ve)
            )

        except Exception as e:
            # System errors
            QMessageBox.critical(
                self, translate.get_translation("system_error"), str(e)
            )

    def delete_entry(self):
        """Remove current selected service"""
        if not self.vault_manager:
            return

        service = self.service_input.text()
        if not service:
            QMessageBox.warning(
                self,
                translate.get_translation("warning_title"),
                translate.get_translation("vault_warn_select_del"),
            )
            return

        confirm = QMessageBox.question(
            self,
            translate.get_translation("vault_confirm_del_title"),
            translate.get_translation("vault_confirm_del_msg").format(service=service),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if self.vault_manager.delete_entry(service):
                QMessageBox.information(
                    self,
                    translate.get_translation("success_title"),
                    translate.get_translation("vault_info_deleted").format(
                        service=service
                    ),
                )
                self.refresh_list()
                self.clear_form()
            else:
                QMessageBox.warning(
                    self,
                    translate.get_translation("error_title"),
                    translate.get_translation("vault_err_del_failed"),
                )
