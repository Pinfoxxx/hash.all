import traceback

from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QTabWidget

from crypto.crypto import CryptoManager
from gui_v2.breach_tab import CheckTab
from gui_v2.config import cfg
from gui_v2.generator_tab import GeneratorTab
from gui_v2.login_window import LoginWindow
from gui_v2.settings_tab import SettingsTab
from gui_v2.translator import translate
from gui_v2.vault_tab import VaultTab
from keys.vault import VaultManager


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
        self.setFixedSize(400, 350)
        self.center_window()

        # Protection from garbage collector (objects links)
        self.crypto_manager = None
        self.vault_manager = None

    def on_login_success(self):
        """Slot which initializing logic if success"""
        username = self.login_screen.name_input.text()
        password = self.login_screen.pass_input.text()
        try:
            # print("Login successful. Initializing managers...")  # Just for debugging
            cfg.load_user_config(username)
            print(f"Loaded configuration for user: {username}")

            # Loading translates
            translate.load_language()

            # Initializing CryptoManager
            self.crypto_manager = CryptoManager(password=password)

            # Initializing VaultManager
            self.vault_manager = VaultManager(
                username=username, crypto_manager=self.crypto_manager
            )

            # Build interface
            self.setup_main()

            if self.stack.count() < 2:
                raise Exception("Main interface tab was not added to stack!")

            # Switch screen
            self.stack.setCurrentIndex(1)
            self.setMaximumSize(16777215, 16777215)
            self.setMinimumSize(900, 600)
            self.resize(900, 600)
            self.center_window()

            # Clear password field in login window
            self.login_screen.pass_input.clear()

            # Update settings tab with user's values
            if hasattr(self, "settings_tab"):
                self.settings_tab.refresh_values()

            # Forced translation when changing languages
            self.on_language_changed()

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(
                self, "Initializing error", f"Failed to load vault:\n{str(e)}"
            )
            self.stack.setCurrentIndex(0)
            self.setFixedSize(400, 350)
            self.center_window()

    def setup_main(self):
        """Creating tabs and injecting dependencies"""
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

        self.generator_tab.password_used_in_vault.connect(
            self.on_password_from_generator
        )

        # Connecting language change signal
        if hasattr(self.settings_tab, "languageChanged"):
            self.settings_tab.languageChanged.connect(self.on_language_changed)

        # Add tabs (with forced translate)
        self.tabs.addTab(self.vault_tab, translate.get_translation("tab_vault"))
        self.tabs.addTab(self.generator_tab, translate.get_translation("tab_generator"))
        self.tabs.addTab(self.breach_tab, translate.get_translation("tab_breach"))
        self.tabs.addTab(self.settings_tab, translate.get_translation("tab_settings"))

        # Add in stack
        self.stack.addWidget(self.tabs)

    def on_language_changed(self):
        """Slot called when changing the language in settings"""
        # Update tab titles
        self.tabs.setTabText(0, translate.get_translation("tab_vault"))
        self.tabs.setTabText(1, translate.get_translation("tab_generator"))
        self.tabs.setTabText(2, translate.get_translation("tab_breach"))
        self.tabs.setTabText(3, translate.get_translation("tab_settings"))

        # Update window title
        self.setWindowTitle(translate.get_translation("window_title"))

        if hasattr(self.vault_tab, "retranslate_ui"):
            self.vault_tab.retranslate_ui()

        if hasattr(self.generator_tab, "retranslate_ui"):
            self.generator_tab.retranslate_ui()

        if hasattr(self.breach_tab, "retranslate_ui"):
            self.breach_tab.retranslate_ui()

    def center_window(self):
        """Center window"""
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def on_password_from_generator(self, password):
        """Switch to vault tab and paste password"""
        self.tabs.setCurrentIndex(0)
        self.vault_tab.pass_input.setText(password)
        self.vault_tab.pass_input.setFocus()
