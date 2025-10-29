import re

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# String with additional secure check
class SecureString(str):

    @classmethod
    def validate_secure_str(cls, value: str, field_name: str) -> str:

        if not value:
            raise ValueError(f"{field_name} cannot be empty!")

        if len(value) > 1024:
            raise ValueError(f"{field_name} is too long!")

        # Checking for dangerous injection symbols (r is for RAW str)
        dangerous_patterns = [
            r"\.\./",  # Path traversal
            r"<script",  # XSS Attack
            r"javascript:"  # XSS Attack
            r"vbscript:"  # XSS Attack
            r"on\w+\s*=",  # Event handlers
        ]

        # re - is a regular
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"{field_name} contains potentially dangerous pattern")

        return value
