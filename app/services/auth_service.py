from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

import httpx
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from redis.asyncio import Redis

from app.core.config.settings import settings
from app.core.security.jwt import (
    hash_password, verify_password,
    create_token_pair, decode_token,
    create_access_token, create_refresh_token,
)
from app.core.database.redis import RedisKeys
from app.models.user_model import User, AuthProvider, LanguageChoice, LevelChoice
from app.schemas.auth_schemas import (
    SignupRequest, LoginRequest, GoogleAuthRequest,
    TokenResponse, UserResponse, AuthResponse,
)
from password.dependency.exceptions import AuthException


class AuthService:

    # Signup

    async def signup(
        self,
        data: SignupRequest,
        db: AsyncSession,
        redis: Redis,
    ) -> AuthResponse:
        # Check email uniqueness
        existing_email = await db.scalar(
            select(User).where(User.email == data.email.lower())
        )
        if existing_email:
            raise AuthException.email_already_registered()

        # Check username uniqueness
        existing_username = await db.scalar(
            select(User).where(User.username == data.username.lower())
        )
        if existing_username:
            raise AuthException.username_taken()

        # Map language/level to enum values
        language = None
        if data.selected_language:
            try:
                language = LanguageChoice(data.selected_language)
            except ValueError:
                pass

        level = LevelChoice.BEGINNER
        if data.level:
            try:
                level = LevelChoice(data.level)
            except ValueError:
                pass

        # Create user
        user = User(
            full_name=data.full_name,
            username=data.username.lower(),
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            date_of_birth=data.date_of_birth,
            country=data.country,
            selected_language=language,
            level=level,
            auth_provider=AuthProvider.EMAIL,
            is_verified=False,
            is_active=True,
        )
        db.add(user)
        await db.flush()  # Get user.id without full commit

        # Issue tokens
        tokens = create_token_pair(str(user.id))

        # Store refresh token in Redis
        await self._store_refresh_token(redis, str(user.id), tokens["refresh_token"])

        await db.commit()
        await db.refresh(user)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            ),
            is_new_user=True,
        )

    # Login

    async def login(
        self,
        data: LoginRequest,
        db: AsyncSession,
        redis: Redis,
    ) -> AuthResponse:
        # Find user by email OR username
        identifier = data.identifier.strip().lower()
        user = await db.scalar(
            select(User).where(
                or_(
                    User.email == identifier,
                    User.username == identifier,
                )
            )
        )

        # Always run verify_password even if user not found (prevents timing attacks)
        dummy_hash = "$2b$12$invalidhashfortimingreasonsonlydummydata"
        if not user:
            verify_password(data.password, dummy_hash)
            raise AuthException.invalid_credentials()

        if not user.hashed_password:
            # Google-only account trying to log in with password
            raise AuthException.invalid_credentials()

        if not verify_password(data.password, user.hashed_password):
            raise AuthException.invalid_credentials()

        if not user.is_active:
            raise AuthException.user_inactive()

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)

        # Issue tokens
        tokens = create_token_pair(str(user.id))
        await self._store_refresh_token(redis, str(user.id), tokens["refresh_token"])

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            ),
            is_new_user=False,
        )

    # Google OAuth flow

    async def google_auth(
        self,
        data: GoogleAuthRequest,
        db: AsyncSession,
        redis: Redis,
    ) -> AuthResponse:
        """
        Verify Google ID token from Flutter, then sign up or log in.
        Flutter sends this after the user completes Google Sign-In on device.
        """
        # Verify the token with Google
        google_user = await self._verify_google_token(data.id_token)

        google_id = google_user["sub"]
        email = google_user.get("email", "").lower()
        full_name = google_user.get("name", "")
        avatar_url = google_user.get("picture")
        email_verified = google_user.get("email_verified", False)

        if not email:
            raise AuthException.google_auth_failed("Could not retrieve email from Google")

        # Check if user exists by google_id OR email
        user = await db.scalar(
            select(User).where(
                or_(User.google_id == google_id, User.email == email)
            )
        )

        is_new_user = False

        if user:
            # Existing user — update Google info if needed
            if not user.google_id:
                user.google_id = google_id
                user.auth_provider = AuthProvider.GOOGLE
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            if email_verified:
                user.is_verified = True
            user.last_login_at = datetime.now(timezone.utc)
        else:
            # New user — create account
            is_new_user = True

            # Generate a unique username from name or email
            base_username = self._generate_username(full_name or email.split("@")[0])
            username = await self._ensure_unique_username(base_username, db)

            language = None
            if data.selected_language:
                try:
                    language = LanguageChoice(data.selected_language)
                except ValueError:
                    pass

            level = LevelChoice.BEGINNER
            if data.level:
                try:
                    level = LevelChoice(data.level)
                except ValueError:
                    pass

            user = User(
                full_name=full_name or email.split("@")[0],
                username=username,
                email=email,
                hashed_password=None,
                google_id=google_id,
                avatar_url=avatar_url,
                auth_provider=AuthProvider.GOOGLE,
                is_verified=email_verified,
                is_active=True,
                selected_language=language,
                level=level,
            )
            db.add(user)

        await db.flush()

        # Issue tokens
        tokens = create_token_pair(str(user.id))
        await self._store_refresh_token(redis, str(user.id), tokens["refresh_token"])

        await db.commit()
        await db.refresh(user)

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
            ),
            is_new_user=is_new_user,
        )

    # Refresh token logic

    async def refresh_tokens(
        self,
        refresh_token: str,
        db: AsyncSession,
        redis: Redis,
    ) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise AuthException.refresh_token_invalid()

        if payload.get("type") != "refresh":
            raise AuthException.refresh_token_invalid()

        user_id = payload.get("sub")
        jti = payload.get("jti")

        # Validate refresh token is still stored in Redis
        stored = await redis.get(RedisKeys.refresh_token(user_id))
        if not stored or stored != refresh_token:
            raise AuthException.refresh_token_invalid()

        # Check user still exists and is active
        user = await db.scalar(select(User).where(User.id == user_id))
        if not user or not user.is_active:
            raise AuthException.user_inactive()

        # Rotate: issue new pair, invalidate old refresh token
        tokens = create_token_pair(str(user.id))
        await self._store_refresh_token(redis, str(user.id), tokens["refresh_token"])

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    # Logout

    async def logout(
        self,
        user_id: str,
        access_token: str,
        redis: Redis,
    ) -> None:
        """Blacklist the access token and delete the refresh token."""
        # Delete refresh token from Redis
        await redis.delete(RedisKeys.refresh_token(user_id))

        # Blacklist the access token until its natural expiry
        try:
            payload = decode_token(access_token)
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                ttl = exp - int(datetime.now(timezone.utc).timestamp())
                if ttl > 0:
                    await redis.setex(
                        RedisKeys.blacklisted_token(jti),
                        ttl,
                        "blacklisted",
                    )
        except JWTError:
            pass  # Token already invalid — that's fine

    # Helper methods

    async def _verify_google_token(self, token: str) -> dict:
        """Verify Google ID token and return the payload."""
        try:
            id_info = google_id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.google_client_id,
            )
            return id_info
        except ValueError as e:
            raise AuthException.google_auth_failed(f"Token verification failed: {str(e)}")

    async def _store_refresh_token(
        self,
        redis: Redis,
        user_id: str,
        token: str,
    ) -> None:
        """Store refresh token in Redis with TTL."""
        ttl = settings.refresh_token_expire_days * 24 * 60 * 60
        await redis.setex(RedisKeys.refresh_token(user_id), ttl, token)

    def _generate_username(self, name: str) -> str:
        """Generate a clean username from name."""
        import re
        username = re.sub(r'[^a-zA-Z0-9_]', '', name.lower().replace(" ", "_"))
        return username[:40] if username else "user"

    async def _ensure_unique_username(self, base: str, db: AsyncSession) -> str:
        """Append numbers until username is unique."""
        username = base
        counter = 1
        while True:
            existing = await db.scalar(select(User).where(User.username == username))
            if not existing:
                return username
            username = f"{base}{counter}"
            counter += 1


auth_service = AuthService()