from redis.asyncio import Redis, from_url
from app.core.config.settings import settings
from typing import Optional

# Redis client singleton
redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """FastAPI dependency — returns the Redis client."""
    return redis_client


async def init_redis() -> None:
    """Initialize Redis connection on app startup."""
    global redis_client
    redis_client = await from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis() -> None:
    """Close Redis connection on app shutdown."""
    global redis_client
    if redis_client:
        await redis_client.aclose()


# Redis key helpers

class RedisKeys:
    """Centralized key management — avoids typos and collisions."""

    @staticmethod
    def refresh_token(user_id: str) -> str:
        return f"refresh_token:{user_id}"

    @staticmethod
    def blacklisted_token(jti: str) -> str:
        """For invalidating access tokens on logout."""
        return f"blacklist:{jti}"

    @staticmethod
    def rate_limit(ip: str, endpoint: str) -> str:
        return f"rate_limit:{ip}:{endpoint}"

    @staticmethod
    def email_verification(user_id: str) -> str:
        return f"email_verify:{user_id}"

    @staticmethod
    def password_reset(token: str) -> str:
        return f"pwd_reset:{token}"

    @staticmethod
    def google_oauth_state(state: str) -> str:
        return f"oauth_state:{state}"