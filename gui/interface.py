import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Optional

from ..config import AppConfig


class MainApplication:
    def __init__(self, username: str, password: str):
        self.username = username

        self.app = tk.Tk()
        self.current_serivce: Optional[str] = None
        self.setup_ui()

    def setup_ui(self):
        self.app.title(f"hash.all - {self.username}'s Vault")
        self.app.geometry(AppConfig.DEFAULT_WINDOW_SIZE)
        # self.app.protocol("WM_DELETE_WINDOW", self.secure_exit) # Placeholder

        # Main frame
        main_frame = ttk.Frame(self.app, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Vault tab
        self.vault_frame = ttk.Frame(self.notebook)
        # self.setup_vault_tab() # Placeholder
        self.notebook.add(self.vault_frame, text="Password Vault")

        # Password generator tab
        self.gen_frame = ttk.Frame(self.notebook)
        # self.setup_get_tab() # Placeholder
        self.notebook.add(self.vault_frame, text="Password Generator")

        # HIBP check tab
        self.hibp_frame = ttk.Frame(self.notebook)
        # self.setup_hibp_tab() # Placeholder
        self.notebook.add(self.hibp_frame, text="Leak Check")
