from PySide6.QtWidgets import QMainWindow, QTabWidget

from vault_tab import VaultTab
from generator_tab import GeneratorTab
from breach_tab import CheckTab


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

        # Add tabs
        self.tabs.addTab(self.vault, "Password vault")
        self.tabs.addTab(self.generator, "Password generator")
        self.tabs.addTab(self.breach, "")
