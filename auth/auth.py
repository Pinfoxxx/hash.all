import os
import json
import secrets
import bcrypt
from pathlib import Path

from models.auth_model import UserRegModel, UserLoginModel, AuthRespModel
from config import SecurityConfig, AppConfig
from .limiter import RateLimiter


class AuthManager:
    def __init__(self, db_path: Path = Path("users.json")):
        self.db_path = db_path
        self.rate_limiter = RateLimiter()
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        if not self.db_path.exists():
            with open(self.db_path, "w") as f:
                json.dump({}, f)
            self.db_path.chmod(AppConfig.SECURE_FILE_MODE)

    def _get_pepper(self) -> str:
        if not SecurityConfig.PEPPER_PATH.exists():
            pepper = secrets.token_hex(32)
            with open(SecurityConfig.PEPPER_PATH, "w") as f:
                f.write(pepper)
            SecurityConfig.PEPPER_PATH.chmod(AppConfig.SECURE_FILE_MODE)

        with open(SecurityConfig.PEPPER_PATH, "r") as f:
            return f.read().strip()

    def register_user(self, user_data: UserRegModel) -> AuthRespModel:
        try:
            with open(self.db_path, "r") as f:
                users = json.load(f)

            if user_data.username in users:
                return AuthRespModel(
                    success=False,
                    message="This username already exist",
                    lockout_time=None,
                    remaining_attempts=None,
                )

            pepper = self._get_pepper()
            salted_password = user_data.password + pepper

            hashed = bcrypt.hashpw(
                salted_password.encode("utf-8"),
                bcrypt.gensalt(rounds=SecurityConfig.BCRYPT_ROUNDS),
            )

            users[user_data.username] = {
                "hash": hashed.decode("utf-8"),
                "created_at": (
                    os.path.getctime(self.db_path)
                    if self.db_path.exists()
                    else os.path.getctime(__file__)
                ),
            }

            with open(self.db_path, "w") as f:
                json.dump(users, f)

            return AuthRespModel(
                success=True,
                message="Registration successful",
                lockout_time=None,
                remaining_attempts=None,
            )

        except Exception as e:
            return AuthRespModel(
                success=False,
                lockout_time=None,
                remaining_attempts=None,
                message=f"Registration failed: {str(e)}",
            )