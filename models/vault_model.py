import time
from datetime import datetime
from typing import Dict

from pydantic import Field, field_validator, model_validator

from gui_v2.config import cfg

from .string_model import BaseSecureModel, SecureString


# Entry model for work with unencrypted data
class VaultEntryModel(BaseSecureModel):
    service: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., examples=["SuperSecretPass123!"])
    notes: str = Field(default="", json_schema_extra={"skip_secure_validation": True})
    created_at: float = Field(default_factory=time.time)

    # Service validation
    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        return SecureString.validate_secure_str(v, "Service")

    # Username validation
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return SecureString.validate_secure_str(v, "Username")

    # Password validation
    @field_validator("password")
    @classmethod
    def validate_pwd(cls, v: str) -> str:
        if len(v) > cfg.data.MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"Password exceeds max length of {cfg.data.MAX_PASSWORD_LENGTH}"
            )
        return SecureString.validate_secure_str(v, "Password")

    # Timestamp validation
    @field_validator("created_at")
    @classmethod
    def validate_timestamp(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Timestamp cannot be lower than 0")
        # Timestamp cannot be more than 1 hour in the future
        if v > time.time() + 3600:
            raise ValueError("Timestamp cannot be in the future")
        return v

    # Returns created_at as datetime object
    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_at)


# Entry model for work with encrypted data
class EncryptedVaultEntryModel(BaseSecureModel):
    service: str = Field(...)  # Unencrypted
    username: str = Field(...)  # Encrypted
    password: str = Field(...)  # Encrypted
    notes: str = Field(...)  # Encrypted
    created_at: float = Field(...)  # Unencrypted


# Vault model for work with metadata
class VaultMetadataModel(BaseSecureModel):
    version: str = Field(default="1.0.0")
    created: float = Field(...)
    last_modified: float = Field(default_factory=time.time)
    entry_count: int = Field(default=0)


# Vault model for work with all data (includes metadata)
class VaultDataModel(BaseSecureModel):
    metadata: VaultMetadataModel = Field(...)
    entries: Dict[str, EncryptedVaultEntryModel] = Field(default_factory=dict)

    # Validate entry count
    @model_validator(mode="after")
    def validate_entry_count(self) -> "VaultDataModel":
        actual_count = len(self.entries)
        if self.metadata.entry_count != actual_count:
            self.metadata.entry_count = actual_count
        return self
