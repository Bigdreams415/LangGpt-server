from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT token utilities

def create_access_token(
    subject: str,              # user_id as string
    extra_claims: dict = {},
) -> str:
    """Create a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "jti": str(uuid4()),   # Unique token ID (for blacklisting)
        "type": "access",
        **extra_claims,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "jti": str(uuid4()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises JWTError on failure."""
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def get_token_jti(token: str) -> Optional[str]:
    """Extract JTI from token without full validation (for blacklisting)."""
    try:
        payload = decode_token(token)
        return payload.get("jti")
    except JWTError:
        return None


def create_token_pair(user_id: str, extra_claims: dict = {}) -> dict:
    """Create both access and refresh tokens at once."""
    return {
        "access_token": create_access_token(str(user_id), extra_claims),
        "refresh_token": create_refresh_token(str(user_id)),
        "token_type": "bearer",
    }