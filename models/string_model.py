import re
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


# BaseModel link
class Base(BaseModel):
    pass


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
            r"\.\./",       # Path traversal
            r"<script",     # XSS Attack
            r"javascript:", # XSS Attack
            r"vbscript:",   # XSS Attack
            r"on\w+\s*=",   # Event handlers
        ]

        # re - is a regular
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"{field_name} contains potentially dangerous pattern")

        return value


class BaseSecureModel(Base):

    model_config = ConfigDict(
        validate_assignment=True,  # Check assignment
        extra="forbid",            # Prohibit additional fields
        str_strip_whitespace=True, # Remove whitespaces
        str_min_length=0,          # Min str length (0 allows empty notes)
        str_max_length=1024,       # Max str length
        frozen=False,              # Allow changing models after creation
    )

    # Automatic str secure check with SecureString class
    @model_validator(mode="before")
    @classmethod
    def validate_all_str(cls, data: Any) -> Any:
        # Check instance
        if isinstance(data, dict):
            for field_name, value in data.items():
                if isinstance(value, str) and field_name in cls.model_fields:
                    
                    # 1. Explicitly skip "notes" to allow empty values
                    if field_name == "notes":
                        continue

                    field_info = cls.model_fields[field_name]
                    skip = False

                    # 2. Check for skip flag in json_schema_extra
                    if field_info.json_schema_extra:
                        if isinstance(field_info.json_schema_extra, dict):
                            skip = field_info.json_schema_extra.get("skip_secure_validation", False)
                    
                    # Check legacy attribute (fallback)
                    if not skip and getattr(field_info, "skip_secure_validation", False):
                        skip = True

                    if skip:
                        continue
                    
                    # 3. Validate strict fields (Service, Username, Password)
                    SecureString.validate_secure_str(value, field_name)

        return data

    # Secure model dump with clear sensitive fields
    def model_dump_secure(self, **kwargs) -> dict:
        result = self.model_dump(**kwargs)

        # Mask sensitive fields from result
        sensitive_fields = ["password", "secret", "key", "token"]
        for field in sensitive_fields:
            if field in result and result[field]:
                result[field] = "***SUCCESFULLY MASKED***"

        return result