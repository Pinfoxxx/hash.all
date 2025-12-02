import tkinter as tk
from tkinter import ttk, messagebox
import threading

from auth.auth import AuthManager
from models.auth_model import UserLoginModel, UserRegModel, AuthRespModel

from config import AppConfig


class LoginWindow:

    def __init__(self):
        self.app = tk.Tk()
        self.auth_manager = AuthManager()
        self.setup_gui()

    # GUI setup method
    def setup_gui(self):
        # Main attributes
        self.app.title("hash.all - secure login")
        self.app.geometry(AppConfig.DEFAULT_WINDOW_SIZE)
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

        # Attempts counter
        self.attempts_label = ttk.Label(main_frame, text="", foreground="orange")
        self.attempts_label.pack(pady=2)

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
        self.attempts_label.config(text="")

        # Run auth thread method
        def login_thread():
            try:
                login_data = UserLoginModel(username=username, password=password)
                response = self.auth_manager.verify_user(login_data)

                self.app.after(0, lambda: self.auth_callback(response))
            except Exception as e:
                self.app.after(
                    0,
                    lambda: self.auth_callback(
                        AuthRespModel(
                            success=False,
                            message=f"Validation error: {str(e)}",
                            remaining_attempts=None,
                            lockout_time=None,
                        )
                    ),
                )

        threading.Thread(target=login_thread, daemon=True).start()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.config(text="Please enter both username and password")
            return

        self.set_gui_state(disabled=True)
        self.status_label.config(text="Registering...")

        def register_thread():
            try:
                user_data = UserRegModel(username=username, password=password)
                response = self.auth_manager.register_user(user_data)

                self.app.after(0, lambda r=response: self.register_callback(r))

            except Exception as e:
                error_msg = f"Validation error: {str(e)}"
                self.app.after(
                    0,
                    lambda: self.register_callback(
                        AuthRespModel(
                            success=False,
                            message=error_msg,
                            remaining_attempts=None,
                            lockout_time=None,
                        )
                    ),
                )

        threading.Thread(target=register_thread, daemon=True).start()

    def auth_callback(self, response: AuthRespModel):
        self.set_gui_state(disabled=False)

        if response.success:
            self.status_label.config(text="Login successful!", foreground="green")
            self.app.after(1000, self.open_main_app)
        else:
            self.status_label.config(text=response.message, foreground="red")
            self.password_entry.delete(0, tk.END)

            if response.remaining_attempts is not None:
                if response.remaining_attempts > 0:
                    self.attempts_label.config(
                        text=f"Remaining attempts: {response.remaining_attempts}",
                        foreground="orange",
                    )
                elif response.lockout_time is not None:
                    self.attempts_label.config(
                        text=f"Account locked for {response.lockout_time} seconds",
                        foreground="red",
                    )
                else:
                    self.attempts_label.config(text="")

    def register_callback(self, response: AuthRespModel):
        self.set_gui_state(disabled=False)

        if response.success:
            self.status_label.config(
                text="Registration successful!", foreground="green"
            )
            self.attempts_label.config(text="")
        else:
            self.status_label.config(text=response.message, foreground="red")
            self.attempts_label.config(text="")
            self.password_entry.delete(0, tk.END)

    # Foolproof n.2 (to make it impossible to spam requests)
    def set_gui_state(self, disabled: bool):
        state = "disabled" if disabled else "normal"
        self.login_btn.config(state=state)
        self.register_btn.config(state=state)
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)

    def open_main_app(self):
        try:
            print("--- Starting main app ---")
            username = self.username_entry.get().strip()
            password = self.password_entry.get()

            self.app.destroy()

            print("Importing interface...")
            from gui.interface import MainApplication

            print("Starting app...")
            app = MainApplication(username, password)
            app.run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error: {e}")

    def run(self):
        self.app.mainloop()
