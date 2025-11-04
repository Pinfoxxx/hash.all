from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Optional

from models.string_model import BaseSecureModel
from config import SecurityConfig


class CryptoConfig(BaseSecureModel):
    salt: bytes
    iterations: int = SecurityConfig.PBKDF2_ITERATIONS


class CryptoManager:
    def __init__(self, password: str, salt: Optional[bytes] = None):
        self.salt = salt or os.urandom(SecurityConfig.SALT_SIZE)
        self.key = self._derive_key(password)
        self.fernet = Fernet(self.key)
        self._secure_wipe(password)

    def _derive_key(self, password: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),  # Hash-func
            length=32,  # Key lenght
            salt=self.salt,  # Unique salt
            iterations=SecurityConfig.PBKDF2_ITERATIONS,  # 100,000 iterations
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def _secure_wipe(self, data: str):
        if hasattr(data, "encode"):
            encoded = data.encode()
            for i in range(len(encoded)):
                encoded_array = bytearray(encoded)
                encoded_array[i] = 0
            del encoded
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
            raise ValueError("Decryption failed - possible tampering detected") from e

    def get_config(self) -> CryptoConfig:
        return CryptoConfig(salt=self.salt)

    def __del__(self):
        if hasattr(self, "key"):
            self._secure_wipe(
                self.key.decode() if hasattr(self.key, "decode") else str(self.key)
            )
