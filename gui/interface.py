import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Optional

from crypto.crypto import CryptoManager
from keys.vault import VaultManager
from pass_gen.pass_gen import PasswordGen
from web_requests.hibp_api import HIBPClient

from ..config import AppConfig


class MainApplication:
    def __init__(self, username: str, password: str):
        self.username = username
        self.crypto = CryptoManager(password)
        self.vault = VaultManager(username, self.crypto)
        self.pass_gen = PasswordGen()
        self.hibp = HIBPClient()

        self.app = tk.Tk()
        self.current_serivce: Optional[str] = None
        self.setup_ui()
        self.refresh_vault_list()

    def setup_ui(self):
        self.app.title(f"hash.all - {self.username}'s Vault")
        self.app.geometry(AppConfig.DEFAULT_WINDOW_SIZE)
        self.app.protocol("WM_DELETE_WINDOW", self.secure_exit)

        # Main frame
        main_frame = ttk.Frame(self.app, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Vault tab
        self.vault_frame = ttk.Frame(self.notebook)
        # self.setup_vault_tab()
        self.notebook.add(self.vault_frame, text="Password Vault")

        # Password generator tab
        self.gen_frame = ttk.Frame(self.notebook)
        # self.setup_get_tab()
        self.notebook.add(self.vault_frame, text="Password Generator")

        # HIBP check tab
        self.hibp_frame = ttk.Frame(self.notebook)
        # self.setup_hibp_tab()

        self.notebook.add(self.vault_frame, text="Password Vault")
        self.notebook.add(self.gen_frame, text="Password Generator")
        self.notebook.add(self.hibp_frame, text="Leak Check")

    def setup_vault_tab(self):
        left_frame = ttk.Frame(self.vault_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(left_frame, text="Stored Services:").pack(anchor=tk.W)

        self.vault_listbox = tk.Listbox(left_frame, width=25, height=20)
        self.vault_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.vault_listbox.bind("<<ListboxSelect>>", self.on_vault_select)

        right_frame = ttk.Frame(self.vault_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(right_frame, text="Service:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.service_var = tk.StringVar()
        self.service_entry = ttk.Entry(
            right_frame, textvariable=self.service_var, width=30
        )
        self.service_entry.grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(right_frame, text="Username:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(
            right_frame, textvariable=self.username_var, width=30
        )
        self.username_entry.grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(right_frame, text="Password:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            right_frame, textvariable=self.password_var, width=30, show="•"
        )
        self.password_entry.grid(row=2, column=1, sticky=tk.W, pady=2)

        self.show_pass_var = tk.BooleanVar()
        ttk.Checkbutton(
            right_frame,
            text="Show Password",
            variable=self.show_pass_var,
            command=self.toggle_password_visibility,
        ).grid(row=3, column=1, sticky=tk.W, pady=2)

        ttk.Label(right_frame, text="Notes:").grid(
            row=4, column=0, sticky=tk.NW, pady=2
        )
        self.notes_text = scrolledtext.ScrolledText(right_frame, width=40, height=8)
        self.notes_text.grid(row=4, column=1, sticky=tk.W, pady=2)

        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Save Entry", command=self.save_entry).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="New Entry", command=self.new_entry).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Delete Entry", command=self.delete_entry).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Refresh", command=self.refresh_vault_list).pack(
            side=tk.LEFT, padx=5
        )

    def setup_get_tab(self): ...  # Placeholder
    def setup_hibp_tab(self): ...  # Placeholder

    def on_vault_select(self, event):
        selection = self.vault_listbox.curselection()
        if not selection:
            return

        # PLACEHOLDER ...............................

    def toggle_password_visibility(self): ...  # Placeholder

    def save_entry(self): ...  # Placeholdrer

    def new_entry(self): ...  # Placeholder

    def delete_entry(self): ...  # Placeholder

    def refresh_vault_list(self): ...  # placeholder

    def secure_exit(self): ...  # placeholder

    def run(self):
        self.app.mainloop()
