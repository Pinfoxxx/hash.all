import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket

from src.config import LOGIN_RES as RESOLUTION


class LoginWindow:

    def __init__(self):
        self.app = tk.Tk()

    # Get IP if possible, otherwise fallback (localhost / 127.0.0.1)
    def get_client_ip(self) -> str:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "127.0.0.1"

    # GUI setup method
    def setup_gui(self):
        # Main attributes
        ...  # title placeholder
        self.app.geometry(RESOLUTION)
        self.app.resizable(False, False)

        # Frames
        main_frame = ttk.Frame(self.app, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Username labels with entries
        ttk.Label(main_frame, text="Username:", font=("Arial", 10)).pack(pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(pady=5)

        # Password labels with entries (the password entered here is hidden)
        ttk.Label(main_frame, text="Password", font=("Arial", 10)).pack(pady=5)
        self.password_entry = ttk.Entry(main_frame, show="•", width=30)
        self.password_entry.pack(pady=5)

        # Login button
        self.login_btn = ttk.Button(main_frame, text="Login", command=self.login)
        self.login_btn.pack(pady=10)

        # Register button
        self.register_btn = ttk.Button(
            main_frame, text="Register", command=self.register
        )
        self.register_btn.pack(pady=5)

        # Display status
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=5)

        # Bind Enter key to login via lambda func
        self.app.bind("<Return>", lambda event: self.login())

    # Login method
    def login(self):

        # Formatting values
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Foolproof n.1
        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return

        self.set_gui_state(disabled=True)
        self.status_label.config(text="Authenticating...")

        # Run auth thread method
        def login_thread(): ...  # placeholder

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return

        self.set_gui_state(disabled=True)
        self.status_label.config(text="Registering...")

        def register_thread(): ...  # placeholder

    def auth_callback(self, response): ...  # placeholder

    # Foolproof n.2 (to make it impossible to spam requests)
    def set_gui_state(self, disabled: bool):
        state = "disabled" if disabled else "normal"
        self.login_btn.config(state=state)
        self.register_btn.config(state=state)
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)

    def open_main_app(self): ...  # placeholder
