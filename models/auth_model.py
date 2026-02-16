import re
from typing import ClassVar, Optional

from pydantic import Field, field_validator, model_validator

from gui_v2.config import cfg

from .string_model import BaseSecureModel, SecureString


# Registration Pydantic model
class UserRegModel(BaseSecureModel):
    username: str = Field(
        ...,  # => required = True
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        examples=["john_doe123"],
    )

    password: str = Field(
        ...,  # => required True
        examples=["UltraSecurePass123!"],
    )

    # Validation patterns
    USERNAME_PATTERN: ClassVar[str] = r"^[a-zA-Z0-9_-]+$"
    PASSWORD_COMPLEXITY: ClassVar[str] = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"
    )

    # Check username patters
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(cls.USERNAME_PATTERN, v):
            raise ValueError(
                "Username can only contain letters, numbers, underscores and hyphens"
            )
        return SecureString.validate_secure_str(v, "Username")

    # Check password complexity
    @field_validator("password")
    @classmethod
    # V is for validate
    def validate_pwd_complex(cls, v: str) -> str:
        if len(v) < cfg.data.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {cfg.data.MIN_PASSWORD_LENGTH} characters long"
            )

        if len(v) > cfg.data.MAX_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be shorter than {cfg.data.MAX_PASSWORD_LENGTH} characters"
            )

        if not re.match(cls.PASSWORD_COMPLEXITY, v):
            raise ValueError(
                "Password must contain: 1 upper, 1 lower, 1 digit, 1 special char"
            )

        if v.lower() == v:
            raise ValueError("Password must contain mixed case characters")

        return SecureString.validate_secure_str(v, "Password")

    # Check whether the username and password values ​​are different
    @model_validator(mode="after")
    def validate_username_pwd_diff(self) -> "UserRegModel":
        if (
            self.username
            and self.password
            and self.username.lower() in self.password.lower()
        ):
            raise ValueError("Password cannot contain username")
        return self


# Login Pydantic model
class UserLoginModel(BaseSecureModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)

    @field_validator("password")
    @classmethod
    def validate_pwd(cls, v: str) -> str:
        return SecureString.validate_secure_str(v, "Password")


# Authentication response Pydantic model
class AuthRespModel(BaseSecureModel):
    success: bool
    message: str
    remaining_attempts: Optional[int] = None
    lockout_time: Optional[int] = None

    # Checking logical sequence
    @model_validator(mode="after")
    def validate_seq(self) -> "AuthRespModel":
        if self.success and self.lockout_time:
            raise ValueError("Successful auth responce cannot have lockout time")
        return self
