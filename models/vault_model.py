import re
import time
from datetime import datetime
from typing import Dict

from pydantic import Field, field_validator, model_validator

from .string_model import BaseSecureModel, SecureString


# Entry model for work with unencrypted data
class VaultEntryModel(BaseSecureModel):
    service: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9\s\.\-_]+$",
        examples=["Google", "GitHub"],
        description="Service name for the credentials",
    )

    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["john_doe123", "test@example.com"],
        description="Username or email for the service",
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=500,
        examples=["SuperSecretPass123!"],
        description="Password for the service",
    )

    notes: str = Field(
        default="",
        min_length=0,
        max_length=1000,
        examples=["Work account"],
        description="Additional notes about this entry",
        json_schema_extra={"skip_secure_validation": True},
    )

    created_at: float = Field(
        default_factory=time.time,
        examples=[1234567890.0],
        description="Timestamp when entry created",
    )

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
    service: str = Field(..., examples=["Google"])  # Unencrypted
    username: str = Field(..., examples=["encrypted_data..."])  # Encrypted
    password: str = Field(..., examples=["encrypted_data..."])  # Encrypted
    notes: str = Field(..., examples=["encrypted_data..."])  # Encrypted
    created_at: float = Field(..., examples=[123456789.0])  # Unencrypted


# Vault model for work with metadata
class VaultMetadataModel(BaseSecureModel):
    version: str = Field(default="1.0.0", examples=["1.0.0"])
    created: float = Field(..., examples=[123456789.0])
    last_modified: float = Field(default_factory=time.time, examples=[123456789.0])
    entry_count: int = Field(default=0, ge=0, examples=[5])

    # Version validatiom
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("Version must be in semantic versioning format")
        return v


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
