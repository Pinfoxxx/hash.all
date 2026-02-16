import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from gui_v2.config import cfg


class CryptoManager:
    def __init__(self, password: str, salt: Optional[bytes] = None):
        self.salt = salt or os.urandom(cfg.data.SALT_SIZE)
        self.key = self._derive_key(password)
        self.fernet = Fernet(self.key)
        self._secure_wipe(password)

    def _derive_key(self, password: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),  # Hash-func
            length=32,  # Key lenght
            salt=self.salt,  # Unique salt
            iterations=cfg.data.PBKDF2_ITERATIONS,  # 100,000 iterations
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _secure_wipe(self, data: str):
        if not data:
            return
        try:
            if isinstance(data, (bytearray, list)):
                for i in range(len(data)):
                    data[i] = 0
        except Exception as e:
            print(f"Error: {e}")
        finally:
            del data

    def encrypt_data(self, data: str) -> str:
        if not data:
            raise ValueError("Data cannot be empty")
        encrypted = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        if not encrypted_data:
            raise ValueError("Encrypted data cannot be empty")
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(
                "Decryption failed - possible tampering or wrong key"
            ) from e

    def __del__(self):
        if hasattr(self, "key"):
            try:
                del self.key
            except AttributeError:
                pass
