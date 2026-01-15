from PySide6.QtWidgets import QMainWindow, QTabWidget, QStackedWidget, QMessageBox

from gui_v2.login_window import LoginWindow
from gui_v2.vault_tab import VaultTab
from gui_v2.generator_tab import GeneratorTab
from gui_v2.breach_tab import CheckTab
from gui_v2.settings_tab import SettingsTab

from keys.vault import VaultManager
from crypto.crypto import CryptoManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("hash.all - password manager")

        # Stacked widget for screen manipulations
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initializing login screen
        self.login_screen = LoginWindow()
        self.login_screen.success.connect(self.on_login_success)

        # Add login screen in stack
        self.stack.addWidget(self.login_screen)

        # Set window size for login_window
        self.resize(400, 350)

        # Protection from garbage collector (objects links)
        self.crypto_manager = None
        self.vault_manager = None

    def on_login_success(self):
        "Slot which initializing logic if success"
        username = self.login_screen.name_input.text()
        password = self.login_screen.pass_input.text()
        try:
            # Initializing CryptoManager
            self.crypto_manager = CryptoManager(password=password)

            # Initializing VaultManager
            self.vault_manager = VaultManager(
                username=username, crypto_manager=self.crypto_manager
            )

            # Build main
            self.setup_main()

            # Switch screen
            self.stack.setCurrentIndex(1)
            self.resize(900, 600)
            self.center_window()

            # Clear password field in login window
            self.login_screen.pass_input.clear()

        except Exception as e:
            QMessageBox.critical(
                self, "Initializing error", f"Failed to load vault: {str(e)}"
            )
            self.stack.setCurrentIndex(0)

    def setup_main(self):
        "Creating tabs and injecting dependencies"
        # Update dependencies if the interface has already been created
        if hasattr(self, "tabs"):
            if self.vault_manager:
                self.vault_tab.set_vault_manager(self.vault_manager)
            return

        # Tabs widget
        self.tabs = QTabWidget()

        # Creating tab objects
        self.vault_tab = VaultTab()
        self.generator_tab = GeneratorTab()
        self.breach_tab = CheckTab()
        self.settings_tab = SettingsTab()

        # Dependency injection
        if self.vault_manager:
            self.vault_tab.set_vault_manager(self.vault_manager)

        # Add tabs
        self.tabs.addTab(self.vault_tab, "Password vault")
        self.tabs.addTab(self.generator_tab, "Password generator")
        self.tabs.addTab(self.breach_tab, "Check breaches")
        self.tabs.addTab(self.settings_tab, "Settings")

    def center_window(self):
        "Center window"
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
