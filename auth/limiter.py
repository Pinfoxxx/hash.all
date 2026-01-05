import time
import threading
from typing import Any, Dict

from models.auth_model import AuthRespModel
from gui_v2.config import SecurityConfig


class RateLimiter:
    def __init__(self):
        self.failed_attempts: Dict[
            str, Dict[str, Any]
        ] = {}  # Failed attempts. Key = username, Arg = count / first_attempt / last_attempt
        self.lock = threading.RLock()  # Reentrant lock
        self.last_cleanup = time.time()  # Last cleanup time

    # Old entries cleanup
    def _cleanup_old_entries(self):
        current_time = time.time()
        if current_time - self.last_cleanup >= SecurityConfig.CLEANUP_INTERVAL:
            with self.lock:
                # Work with failed attempts count
                self.failed_attempts = {
                    username: data
                    for username, data in self.failed_attempts.items()
                    if current_time - data["first_attempt"] < SecurityConfig
                }
                self.last_cleanup = current_time

    # Check limits
    def check_rate_limit(self, username: str) -> tuple[bool, AuthRespModel]:
        self._cleanup_old_entries()
        current_time = time.time()

        with self.lock:
            if username in self.failed_attempts:
                attempts_data = self.failed_attempts[username]

                if (
                    current_time - attempts_data["last_attempt"]
                    < SecurityConfig.LOCKOUT_DURATION
                ):
                    # Full lockout
                    if attempts_data["count"] >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
                        remaining_time = int(
                            SecurityConfig.LOCKOUT_DURATION
                            - (current_time - attempts_data["last_attempt"])
                        )
                        return False, AuthRespModel(
                            success=False,
                            message=f"Too many failed attempts. Try again in {remaining_time} seconds.",
                            lockout_time=remaining_time,
                            remaining_attempts=0,
                        )

                    # Limited access
                    else:
                        remaining_attempts = (
                            SecurityConfig.MAX_LOGIN_ATTEMPTS - attempts_data["count"]
                        )
                        return True, AuthRespModel(
                            success=True,
                            message="Proceed",
                            lockout_time=None,
                            remaining_attempts=remaining_attempts,
                        )

        # Full access
        return True, AuthRespModel(
            success=True,
            message="Proceed",
            remaining_attempts=SecurityConfig.MAX_LOGIN_ATTEMPTS,
            lockout_time=None,
        )

    # Record failed attempt
    def rec_failed_attempt(self, username: str) -> AuthRespModel:
        current_time = time.time()

        with self.lock:
            if username not in self.failed_attempts:
                self.failed_attempts[username] = {
                    "count": 0,
                    "first_attempt": current_time,
                    "last_attempt": current_time,
                }

            data = self.failed_attempts[username]
            data["count"] += 1
            data["last_attempt"] = current_time

            remaining_attempts = SecurityConfig.MAX_LOGIN_ATTEMPTS - data["count"]

            if data["count"] >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
                lockout_time = SecurityConfig.LOCKOUT_DURATION
                return AuthRespModel(
                    success=False,
                    message=f"Sorry, your account locked due to too many failed attempts. Try again in {lockout_time} second.",
                    remaining_attempts=0,
                    lockout_time=lockout_time,
                )

            else:
                return AuthRespModel(
                    success=False,
                    message=f"Invalid credentials. {remaining_attempts} attempts remaining.",
                    remaining_attempts=remaining_attempts,
                    lockout_time=None,
                )

    # Cleanup if success auth
    def clear_attempts(self, username: str):
        with self.lock:
            self.failed_attempts.pop(username, None)
