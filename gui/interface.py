import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Optional

from crypto.crypto import CryptoManager
from keys.vault import VaultManager
from models.vault_model import VaultEntryModel
from pass_gen.pass_gen import PasswordGen
from web_requests.hibp_api import HIBPClient
from web_requests.russian_api.bypass2 import YandexClusterClient

from config import AppConfig


class MainApplication:
    def __init__(self, username: str, password: str):
        self.username = username
        self.crypto = CryptoManager(password)
        self.vault = VaultManager(username, self.crypto)
        self.pass_gen = PasswordGen()
        self.hibp = HIBPClient()

        YANDEX_DIR = "https://disk.yandex.ru/d/O22Pp0Anlf0rRA"
        self.yandex_client = YandexClusterClient(YANDEX_DIR)

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
        self.setup_vault_tab()
        self.notebook.add(self.vault_frame, text="Password Vault")

        # Password generator tab
        self.gen_frame = ttk.Frame(self.notebook)
        self.setup_gen_tab()
        self.notebook.add(self.vault_frame, text="Password Generator")

        # HIBP check tab
        self.hibp_frame = ttk.Frame(self.notebook)
        self.setup_hibp_tab()

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
        ttk.Button(button_frame, text="Clear Entry", command=self.clear_entry).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Delete Entry", command=self.delete_entry).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Refresh", command=self.refresh_vault_list).pack(
            side=tk.LEFT, padx=5
        )

    def setup_gen_tab(self):
        main_frame = ttk.Frame(self.gen_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Password Lenght").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.lenght_var = tk.IntVar(value=16)
        lenght_spin = ttk.Spinbox(
            main_frame, from_=8, to=50, textvariable=self.lenght_var, width=10
        )
        lenght_spin.grid(row=0, column=1, sticky=tk.W, pady=5)

        self.upper_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame, text="Uppercase Letters (A-Z)", variable=self.upper_var
        ).grid(row=1, column=0, sticky=tk.W, pady=2)

        self.lower_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame, text="Lowercase Letters (A-Z)", variable=self.lower_var
        ).grid(row=2, column=0, sticky=tk.W, pady=2)

        self.digits_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Digits (0-9)", variable=self.digits_var).grid(
            row=3, column=0, sticky=tk.W, pady=2
        )

        self.special_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame, text="Special Characters (!@#$%)", variable=self.special_var
        ).grid(row=4, column=0, sticky=tk.W, pady=2)

        ttk.Label(main_frame, text="Generated Password:").grid(
            row=5, column=0, sticky=tk.W, pady=10
        )

        self.generated_pass_var = tk.StringVar()
        pass_entry = ttk.Entry(
            main_frame,
            textvariable=self.generated_pass_var,
            width=40,
            font=("Courier", 10),
        )
        pass_entry.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Button(
            main_frame, text="Generate Password", command=self.generate_password
        ).grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Button(
            main_frame, text="Copy to Clipboard", command=self.copy_to_clipboard
        ).grid(row=7, column=1, sticky=tk.W, padx=5)
        ttk.Button(main_frame, text="Use in Vault", command=self.use_in_vault).grid(
            row=7, column=2, sticky=tk.W, padx=5
        )

        self.use_ru_mode_gen_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main_frame,
            text="Use Russian Bypass",
            variable=self.use_ru_mode_gen_var,
        ).grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=5)

        self.hibp_status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.hibp_status_var).grid(
            row=9, column=0, columnspan=2, sticky=tk.W, pady=5
        )

    def setup_hibp_tab(self):
        main_frame = ttk.Frame(self.hibp_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Check Password Security:").pack(anchor=tk.W, pady=5)

        self.check_pass_var = tk.StringVar()
        check_entry = ttk.Entry(
            main_frame,
            textvariable=self.check_pass_var,
            width=40,
            show="•",
            font=("Courier", 10),
        )
        check_entry.pack(fill=tk.X, pady=5)

        self.use_ru_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main_frame, text="Use Russian Bypass", variable=self.use_ru_mode_var
        ).pack(anchor=tk.W, pady=2)

        ttk.Button(
            main_frame, text="Check Password", command=self.check_password_breach
        ).pack(anchor=tk.W, pady=5)

        self.hibp_result_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.hibp_result_var, wraplength=400).pack(
            anchor=tk.W, pady=10
        )

        self.show_hibp_pass_var = tk.BooleanVar()
        ttk.Checkbutton(
            main_frame,
            text="Show Password",
            variable=self.show_hibp_pass_var,
            command=lambda: self.toggle_password_visibility_hibp(check_entry),
        ).pack(anchor=tk.W)

    def refresh_vault_list(self):
        self.vault_listbox.delete(0, tk.END)
        services = self.vault.list_services()
        for service in sorted(services):
            self.vault_listbox.insert(tk.END, service)

    def on_vault_select(self, event):
        selection = self.vault_listbox.curselection()
        if not selection:
            return

        service = self.vault_listbox.get(selection[0])
        self.current_serivce = service

        entry = self.vault.get_entry(service)
        if entry:
            self.service_var.set(entry.service)
            self.username_var.set(entry.username)
            self.password_var.set(entry.password)
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(1.0, entry.notes)

    def save_entry(self):
        service = self.service_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get()
        notes = self.notes_text.get(1.0, tk.END).strip()

        if not service or not username or not password:
            messagebox.showerror("Error", "Service, username and password are required")
            return

        try:
            entry = VaultEntryModel(
                service=service, username=username, password=password, notes=notes
            )

            self.vault.add_entry(entry)
            self.refresh_vault_list()
            messagebox.showinfo("Success", "Entry saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {str(e)}")

    def clear_entry(self):
        self.current_serivce = None
        self.service_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.notes_text.delete(1.0, tk.END)
        self.vault_listbox.selection_clear(0, tk.END)

    def delete_entry(self):
        if not self.current_serivce:
            messagebox.showerror("Error", "No entry selected")
            return

        if messagebox.askyesno("Confirm", f"Delete entry for {self.current_serivce}?"):
            try:
                self.vault.delete_entry(self.current_serivce)
                self.refresh_vault_list()
                self.clear_entry()
                messagebox.showinfo("Success", "Entry deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete entry: {str(e)}")

    def toggle_password_visibility(self):
        if self.show_pass_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")

    def toggle_password_visibility_hibp(self, entry_widget):
        if self.show_hibp_pass_var.get():
            entry_widget.config(show="")
        else:
            entry_widget.config(show="•")

    def generate_password(self):
        try:
            password = self.pass_gen.generate(
                lenght=self.lenght_var.get(),
                use_upper=self.upper_var.get(),
                use_lower=self.lower_var.get(),
                use_digits=self.digits_var.get(),
                use_special=self.special_var.get(),
            )
            self.generated_pass_var.set(password)
            self.hibp_status_var.set("Checking HIBP...")

            threading.Thread(
                target=self.check_generated_password_breach, daemon=True
            ).start()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def check_generated_password_breach(self):
        password = self.generated_pass_var.get()
        if not password:
            return

        use_bypass = self.use_ru_mode_gen_var.get()

        msg = "Scanning Yandex DB..." if use_bypass else "Checking API..."
        self.app.after(0, lambda: self.hibp_status_var.set(msg))

        try:
            if use_bypass:
                if not hasattr(self, "yandex_client"):
                    self.hibp_status_var.set("Error: Yandex client not init")
                    return

                count = self.yandex_client.check_password(password)
            else:
                count = self.hibp.check_password_breach(password)

            if count > 0:
                self.app.after(
                    0,
                    lambda: self.hibp_status_var.set(
                        f"⚠️ This password has been breached {count} times!"
                    ),
                )
            elif count == 0:
                self.app.after(
                    0,
                    lambda: self.hibp_status_var.set(
                        "✅ Password not found in known breaches"
                    ),
                )
            else:
                self.app.after(
                    0,
                    lambda: self.hibp_status_var.set(
                        "❌ Could not check HIBP (network error)"
                    ),
                )
        except Exception as e:
            error_msg = str(e)
            self.app.after(0, lambda: self.hibp_status_var.set(f"Error: {error_msg}"))

    def check_password_breach(self):
        password = self.check_pass_var.get()
        if not password:
            messagebox.showerror("Error", "Please enter a password to check")
            return

        use_bypass = self.use_ru_mode_var.get()
        self.hibp_result_var.set(
            "Checking..." if not use_bypass else "Scanning Yandex DB..."
        )

        def check_thread():
            try:
                if use_bypass:
                    if not self.yandex_client.is_ready:
                        self.yandex_client._initialize_cluster()
                    count = self.yandex_client.check_password(password)
                else:
                    count = self.hibp.check_password_breach(password)

                if count > 0:
                    result = f"⚠️ This password has been found in {count} data breaches!\nDo NOT use this password!"
                elif count == 0:
                    result = "✅ Password not found in known breaches"
                else:
                    result = "❌ Could not check password (network error)"
            except Exception as e:
                result = f"Error: {str(e)}"

            self.app.after(0, lambda: self.hibp_result_var.set(result))

        threading.Thread(target=check_thread, daemon=True).start()

    def copy_to_clipboard(self):
        password = self.generated_pass_var.get()
        if password:
            self.app.clipboard_clear()
            self.app.clipboard_append(password)
            messagebox.showinfo("Success", "Password copied to vault form")

    def use_in_vault(self):
        password = self.generated_pass_var.get()
        if password:
            self.notebook.select(0)
            self.password_var.set(password)
            messagebox.showinfo("Success", "Passwor1d copied to vault form")

    def secure_exit(self):
        self.password_var.set("")
        self.generated_pass_var.set("")
        self.check_pass_var.set("")

        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.app.destroy()

    def run(self):
        self.app.mainloop()
