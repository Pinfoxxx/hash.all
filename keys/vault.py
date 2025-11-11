import json
import os
import tempfile
from pathlib import Path
from typing import Optional, List

from models.vault_model import (
    VaultEntryModel,
    VaultDataModel,
    VaultMetadataModel,
    EncryptedVaultEntryModel,
)
from crypto.crypto import CryptoManager
from config import AppConfig, SecurityConfig


class VaultManager:
    # Initialization
    def __init__(self, username: str, crypto_manager: CryptoManager):
        self.vault_path = Path(f"{username}{SecurityConfig.VAULT_EXTENSION}")
        self.crypto = crypto_manager
        self._ensure_vault_exists()

    # Check exist vault / create new if not exist
    def _ensure_vault_exists(self):
        if not self.vault_path.exists():
            vault_data = VaultDataModel(
                metadata=VaultMetadataModel(created=os.path.getctime(__file__)),
                entries={},
            )
            self._save_vault(vault_data)

    # Loading exist vault / or error
    def _load_vault(self) -> VaultDataModel:
        try:
            with open(self.vault_path, "r") as f:
                data = json.load(f)
            return VaultDataModel(**data)
        except (json.JSONDecodeError, FileNotFoundError):
            return VaultDataModel(
                metadata=VaultMetadataModel(created=os.path.getctime(__file__))
            )

    # Atomic save: tempfile, only owner can get this data
    def _save_vault(self, vault_data: VaultDataModel):
        with tempfile.NamedTemporaryFile(
            mode="w", dir=self.vault_path.parent, delete=False
        ) as tmp_file:
            json.dump(vault_data.model_dump(), tmp_file, indent=2)
            tmp_path = Path(tmp_file.name)

        tmp_path.replace(self.vault_path)
        self.vault_path.chmod(AppConfig.SECURE_FILE_MODE)

    # Add entry / save updated vault
    def add_entry(self, entry: VaultEntryModel) -> bool:
        try:
            vault_data = self._load_vault()

            encrypted_entry = EncryptedVaultEntryModel(
                service=entry.service,
                username=self.crypto.encrypt_data(entry.username),
                password=self.crypto.encrypt_data(entry.password),
                notes=self.crypto.encrypt_data(entry.notes),
                created_at=entry.created_at,
            )

            vault_data.entries[entry.service] = encrypted_entry
            vault_data.metadata.entry_count = len(vault_data.entries)
            vault_data.metadata.last_modified = entry.created_at

            self._save_vault(vault_data)
            return True

        except Exception as e:
            raise ValueError(f"Failed to add entry: {str(e)}")

    # Get entry by service name / return decrypt data or None if error
    def get_entry(self, service: str) -> Optional[VaultEntryModel]:
        vault_data = self._load_vault()

        if service not in vault_data.entries:
            return None

        encrypted = vault_data.entries[service]
        try:
            return VaultEntryModel(
                service=service,
                username=self.crypto.decrypt_data(encrypted.username),
                password=self.crypto.decrypt_data(encrypted.password),
                notes=self.crypto.decrypt_data(encrypted.notes),
                created_at=encrypted.created_at,
            )
        except ValueError:
            return None

    # Get listed services / entries
    def list_services(self) -> List[str]:
        vault_data = self._load_vault()
        return list(vault_data.entries.keys())

    # Delete entry. Returns True if success, or False if fault
    def delete_entry(self, service: str) -> bool:
        vault_data = self._load_vault()

        if service in vault_data.entries:
            del vault_data.entries[service]
            vault_data.metadata.entry_count = len(vault_data.entries)
            self._save_vault(vault_data)
            return True
        return False

    # Get metadata from vault
    def get_vault_info(self) -> VaultMetadataModel:
        vault_data = self._load_vault()
        return vault_data.metadata
