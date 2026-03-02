from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis
from jose import JWTError

from app.core.security.jwt import decode_token
from app.core.database.database import get_db
from app.core.database.redis import get_redis, RedisKeys
from app.models.user_model import User
from password.dependency.exceptions import AuthException

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    """
    FastAPI dependency — extracts and validates JWT from Authorization header.
    Use this in any protected route.
    """
    if not credentials:
        raise AuthException.invalid_token()

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError:
        raise AuthException.invalid_token()

    if payload.get("type") != "access":
        raise AuthException.invalid_token()

    user_id: str = payload.get("sub")
    jti: str = payload.get("jti")

    if not user_id or not jti:
        raise AuthException.invalid_token()

    # Check if token has been blacklisted (logged out)
    is_blacklisted = await redis.exists(RedisKeys.blacklisted_token(jti))
    if is_blacklisted:
        raise AuthException.token_blacklisted()

    # Load user from DB
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise AuthException.user_not_found()

    if not user.is_active:
        raise AuthException.user_inactive()

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Same as get_current_user but extra-explicit about requiring active user."""
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require superuser/admin access."""
    if not current_user.is_superuser:
        raise AuthException.not_authorized()
    return current_user


def get_token_from_request(request: Request) -> str:
    """Extract raw token string from request (for logout)."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return ""