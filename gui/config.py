import json
import os
import platform
import stat
from dataclasses import asdict, dataclass
from pathlib import Path

"""
Explanation:
    We use the .json file format to conveniently store user configuration settings.
"""


@dataclass
class Config:
    """Main configuration dataclass (validation)"""

    # Safe limits (defaults)
    PBKDF2_ITERATIONS: int = 100000
    BCRYPT_ROUNDS: int = 14
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    SALT_SIZE: int = 32
    PEPPER_PATH: str = ".pepper"
    VAULT_EXTENSION: str = ".vault"
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION: int = 900
    CLEANUP_INTERVAL: int = 3600

    # Application settings
    APP_NAME: str = "hash.all (test branch)"
    VERSION: str = "1.0b"
    DEFAULT_WINDOW_SIZE: str = "800x600"
    LANGUAGE: str = "English"

    # API settings
    HIBP_REQUEST_DELAY: float = 1.6
    HIBP_TIMEOUT: int = 10
    YANDEX_DIR: str = "https://disk.yandex.ru/d/O22Pp0Anlf0rRA"


class ConfigManager:
    """Configration manager"""

    def __init__(self):
        self.config_dir = self._get_config_path()
        self._ensure_dir_exists(self.config_dir)
        self.config_file = (
            self.config_dir / "config_default.json"
        )  # Load default config while user logging in

        self.vaults_dir = self.config_dir / "vaults"
        self._ensure_dir_exists(self.vaults_dir)

        self.data = Config()
        self.load()

    def _get_config_path(self) -> Path:
        """Determines the base config path depending on the OS"""
        home = Path.home()

        if platform.system() == "Windows":  # Windows
            path = Path(os.getenv("APPDATA", home / "AppData/Roaming")) / "hash.all"
        else:  # Linux / MacOS and etc.
            path = home / ".config" / "hash.all"

        return path

    def _ensure_dir_exists(self, path: Path):
        """Creates directory with rights if it doesn't exists"""
        # Make dir with admin rights / 700 rights (only for owner)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            if platform.system() != "Windows":
                os.chmod(path, stat.S_IRWXU)  # rights rwx------

    def load_user_config(self, username: str):
        self.config_file = self.config_dir / f"config_{username}.json"
        self.load()

    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)

                    for key, value in loaded_data.items():
                        if hasattr(self.data, key):
                            setattr(self.data, key, value)
            except Exception:
                self.reset()  # Reset if file corrupted
        else:
            self.save()  # Otherwise we save it

    def save(self):
        try:
            # Use a tempfile for write to avoid file corruption
            temp_file = self.config_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.data), f, indent=4)

            # Chmod for Linux / MacOS. Windows don't need this
            if platform.system() != "Windows":
                os.chmod(temp_file, stat.S_IRUSR | stat.S_IWUSR)  # rights rw-------

            os.replace(temp_file, self.config_file)
        except Exception as e:
            print(f"Critical error saving config: {e}")

    def reset(self):
        self.data = Config()
        self.save()


# Create an instance
cfg = ConfigManager()
