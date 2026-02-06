import json
import os
from pathlib import Path
from typing import ClassVar

# Many of these constants are placeholders, but will be used soon


# Security configuration
class SecurityConfig:
    PBKDF2_ITERATIONS: ClassVar[int] = 100000  # Count of iterations for PBKDF2
    BCRYPT_ROUNDS: ClassVar[int] = 14  # Cost factor for bcrypt
    MIN_PASSWORD_LENGHT: ClassVar[int] = 12  # Minimal password lenght
    MAX_PASSWORD_LENGHT: ClassVar[int] = 128  # Maximum password lenght
    SALT_SIZE: ClassVar[int] = 32  # Salt size in bytes
    PEPPER_PATH: ClassVar[Path] = Path(".pepper")  # Path to pepper-file
    VAULT_EXTENSION: ClassVar[str] = ".vault"  # Vault extension

    # Rate limitting
    MAX_LOGIN_ATTEMPTS: ClassVar[int] = 5  # Maximum login attempts
    LOCKOUT_DURATION: ClassVar[int] = 900  # 15 minutes block
    CLEANUP_INTERVAL: ClassVar[int] = 3600  # Cleanup after 60 minutes


# App configuration
class AppConfig:
    # Base settings
    APP_NAME: ClassVar[str] = "hash.all"  # App name
    VERSION: ClassVar[str] = "0.5"  # App version
    DEFAULT_WINDOW_SIZE: ClassVar[str] = "800x600"  # App window_size
    LANGUAGE: ClassVar[str] = "English"

    # File permissions / only owner
    SECURE_FILE_MODE: ClassVar[int] = 0o600

    # API settings
    HIBP_REQUEST_DELAY: ClassVar[float] = 1.6  # API requests delay
    HIBP_TIMEOUT: ClassVar[int] = 10  # API requests timeout

    # Bypass settings
    YANDEX_DIR: ClassVar[str] = "https://disk.yandex.ru/d/O22Pp0Anlf0rRA"


def load_config():
    "Load configation from file or create config file"
    config_path = "settings.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Loading AppConfig
                app_data = data.get("AppConfig", {})
                AppConfig.HIBP_REQUEST_DELAY = app_data.get(
                    "HIBP_REQUEST_DELAY", AppConfig.HIBP_REQUEST_DELAY
                )
                AppConfig.HIBP_TIMEOUT = app_data.get(
                    "HIBP_TIMEOUT", AppConfig.HIBP_TIMEOUT
                )
                AppConfig.LANGUAGE = app_data.get("LANGUAGE", AppConfig.LANGUAGE)

                # Loading SecurityConfig
                sec_data = data.get("SecurityConfig", {})
                SecurityConfig.PBKDF2_ITERATIONS = sec_data.get(
                    "PBKDF2_ITERATIONS", SecurityConfig.PBKDF2_ITERATIONS
                )
                SecurityConfig.BCRYPT_ROUNDS = sec_data.get(
                    "BCRYPT_ROUNDS", SecurityConfig.BCRYPT_ROUNDS
                )
                SecurityConfig.SALT_SIZE = sec_data.get(
                    "SALT_SIZE", SecurityConfig.SALT_SIZE
                )
                SecurityConfig.LOCKOUT_DURATION = sec_data.get(
                    "LOCKOUT_DURATION", SecurityConfig.LOCKOUT_DURATION
                )
        except Exception as e:
            print(f"Configuration saving error: {e}")


load_config()
