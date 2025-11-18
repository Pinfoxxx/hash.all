import re
from typing import ClassVar, Optional

from pydantic import Field, field_validator, model_validator

from .string_model import BaseSecureModel, SecureString


# Registration Pydantic model
class UserRegModel(BaseSecureModel):
    username: str = Field(
        ...,  # => required = True
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        examples=["john_doe123"],
        description="Username for registration",
    )

    password: str = Field(
        ...,  # => required True
        min_length=12,
        max_length=128,
        examples=["UltraSecurePass123!"],
        description="Strong password meeting complexity requirements",
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
        if not re.match(cls.PASSWORD_COMPLEXITY, v):
            raise ValueError(
                "Password must contain at least:\n1 uppercase letter, 1 lowercase letter, 1 number and 1 special character"
            )

        if v.lower() == v:
            raise ValueError("Password must contain mixed case characters")

        if len(set(v)) < 8:
            raise ValueError("Password must contain at least 8 unique characters")

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
    username: str = Field(..., min_length=3, max_length=50, examples=["john_doe123"])

    password: str = Field(
        ..., min_length=12, max_length=128, examples=["UltraSecurePass123!"]
    )

    @field_validator("password")
    @classmethod
    def validate_pwd(cls, v: str) -> str:
        return SecureString.validate_secure_str(v, "Password")


# Authentication response Pydantic model
class AuthRespModel(BaseSecureModel):
    success: bool = Field(..., examples=[True, False])
    message: str = Field(..., examples=["Login successful", "Invalid credentials"])
    remaining_attempts: Optional[int] = Field(None, ge=0, le=5, examples=[3])
    lockout_time: Optional[int] = Field(None, ge=0, examples=[300])

    # Checking logical sequence
    @model_validator(mode="after")
    def validate_seq(self) -> "AuthRespModel":
        if self.success and self.lockout_time:
            raise ValueError("Successful auth responce cannot have lockout time")
        return self
