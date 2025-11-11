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
    VERSION: ClassVar[str] = "placeholder"  # App version
    DEFAULT_WINDOW_SIZE: ClassVar[str] = "800x600"  # App window_size

    # File permissions / only owner
    SECURE_FILE_MODE: ClassVar[int] = 0o600

    # API settings
    HIBP_REQUEST_DELAY: ClassVar[float] = 1.6  # API requests delay
    HIBP_TIMEOUT: ClassVar[int] = 10  # API requests timeout
