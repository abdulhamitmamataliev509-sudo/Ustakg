"""Security helpers: password hashing and JWT token creation."""
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _create_token(subject: Union[str, Any], token_type: str, expires_minutes: int) -> str:
    """Create a signed JWT with the given type and lifetime."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    subject: Union[str, Any], expires_delta: Union[timedelta, None] = None
) -> str:
    """Create a short-lived JWT access token for the given subject."""
    minutes = (
        int(expires_delta.total_seconds() // 60)
        if expires_delta
        else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return _create_token(subject, token_type="access", expires_minutes=minutes)


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Union[timedelta, None] = None
) -> str:
    """Create a long-lived JWT refresh token for the given subject."""
    minutes = (
        int(expires_delta.total_seconds() // 60)
        if expires_delta
        else settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    return _create_token(subject, token_type="refresh", expires_minutes=minutes)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)
