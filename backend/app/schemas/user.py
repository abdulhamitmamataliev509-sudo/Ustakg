"""Auth & user schemas."""
import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import UserRole

# Kyrgyzstan mobile format: +996 followed by 9 digits.
PHONE_PATTERN = r"^\+996[0-9]{9}$"


class UserRegister(BaseModel):
    phone_number: str = Field(..., examples=["+996555123456"])
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=120)
    role: UserRole = UserRole.CUSTOMER

    @field_validator("phone_number")
    @classmethod
    def _validate_phone(cls, v: str) -> str:
        if not re.fullmatch(PHONE_PATTERN, v):
            raise ValueError(
                "Phone number must match Kyrgyzstan format +996XXXXXXXXX"
            )
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone_number: str
    full_name: str
    role: UserRole
    is_active: bool
    avatar_url: str | None = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str
