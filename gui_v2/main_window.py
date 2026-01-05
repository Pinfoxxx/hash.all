from PySide6.QtWidgets import QMainWindow, QTabWidget

from gui_v2.vault_tab import VaultTab
from gui_v2.generator_tab import GeneratorTab
from gui_v2.breach_tab import CheckTab
from gui_v2.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("hash.all - password manager")
        self.resize(900, 600)

        # Tabs widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Creating tab objects
        self.vault = VaultTab()
        self.generator = GeneratorTab()
        self.breach = CheckTab()
        self.settings = SettingsTab()

        # Add tabs
        self.tabs.addTab(self.vault, "Password vault")
        self.tabs.addTab(self.generator, "Password generator")
        self.tabs.addTab(self.breach, "Check breaches")
        self.tabs.addTab(self.settings, "Settings")
