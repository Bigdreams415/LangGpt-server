import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import settings
from app.models.notification_model import DevicePlatform, DeviceToken, NotificationPreference
from app.schemas.notification_schemas import NotificationCategory, SendResult

logger = logging.getLogger(__name__)

# Maps each category to its column name on NotificationPreference.
_CATEGORY_FIELD: dict[NotificationCategory, str] = {
    NotificationCategory.DAILY_REMINDERS: "daily_reminders",
    NotificationCategory.STREAK_REMINDERS: "streak_reminders",
    NotificationCategory.LESSON_UPDATES: "lesson_updates",
    NotificationCategory.ACHIEVEMENTS: "achievements",
    NotificationCategory.NEW_CONTENT: "new_content",
    NotificationCategory.MARKETING: "marketing",
}


class NotificationService:
    def __init__(self) -> None:
        self._messaging: Any = None

    # ── Initialization ──────────────────────────────────────────────────────

    def initialize(self, credentials_path: str) -> None:
        if not settings.push_notifications_enabled:
            logger.info("Push notifications disabled by settings; skipping Firebase init")
            return

        if not credentials_path or not Path(credentials_path).exists():
            logger.warning(
                "Firebase credentials not found at '%s'; push notifications disabled",
                credentials_path,
            )
            return

        try:
            import firebase_admin
            from firebase_admin import credentials, messaging

            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            self._messaging = messaging
            logger.info("Firebase initialized successfully")
        except Exception as exc:
            logger.error("Firebase initialization failed: %s", exc)

    @property
    def enabled(self) -> bool:
        return self._messaging is not None

    # ── Device tokens ───────────────────────────────────────────────────────

    async def register_device_token(
        self,
        db: AsyncSession,
        user: Any,
        token: str,
        platform: DevicePlatform,
        device_info: Optional[str] = None,
    ) -> DeviceToken:
        now = datetime.now(timezone.utc)

        existing = await db.scalar(
            select(DeviceToken).where(DeviceToken.token == token)
        )

        if existing:
            # Transfer ownership if the token moved to a different account.
            existing.user_id = user.id
            existing.is_active = True
            existing.last_used_at = now
            existing.platform = platform
            if device_info is not None:
                existing.device_info = device_info
            await db.commit()
            await db.refresh(existing)
            return existing

        row = DeviceToken(
            user_id=user.id,
            token=token,
            platform=platform,
            device_info=device_info,
            last_used_at=now,
        )
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def unregister_device_token(
        self,
        db: AsyncSession,
        user: Any,
        token: str,
    ) -> None:
        await db.execute(
            update(DeviceToken)
            .where(DeviceToken.user_id == user.id, DeviceToken.token == token)
            .values(is_active=False)
        )
        await db.commit()

    # ── Preferences ─────────────────────────────────────────────────────────

    async def get_or_create_preferences(
        self,
        db: AsyncSession,
        user: Any,
    ) -> NotificationPreference:
        row = await db.scalar(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user.id
            )
        )
        if row:
            return row

        row = NotificationPreference(user_id=user.id)
        db.add(row)
        await db.commit()
        await db.refresh(row)
        return row

    async def update_preferences(
        self,
        db: AsyncSession,
        user: Any,
        prefs_in: Any,
    ) -> NotificationPreference:
        row = await self.get_or_create_preferences(db, user)
        for field, value in prefs_in.model_dump(exclude_unset=True).items():
            setattr(row, field, value)
        await db.commit()
        await db.refresh(row)
        return row

    # ── Sending ─────────────────────────────────────────────────────────────

    async def send_to_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        title: str,
        body: str,
        category: NotificationCategory,
        data: Optional[dict[str, Any]] = None,
        image_url: Optional[str] = None,
    ) -> SendResult:
        if not self.enabled:
            return SendResult(success_count=0, failure_count=0, invalidated_tokens=0)

        prefs = await db.scalar(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        if prefs:
            category_field = _CATEGORY_FIELD[category]
            if not prefs.push_enabled or not getattr(prefs, category_field):
                return SendResult(success_count=0, failure_count=0, invalidated_tokens=0)

        tokens = list(
            await db.scalars(
                select(DeviceToken).where(
                    DeviceToken.user_id == user_id,
                    DeviceToken.is_active.is_(True),
                )
            )
        )
        if not tokens:
            return SendResult(success_count=0, failure_count=0, invalidated_tokens=0)

        payload_data = dict(data or {})
        payload_data.setdefault("route", "/")
        payload_data["category"] = category.value
        payload_data["sent_at"] = datetime.now(timezone.utc).isoformat()
        payload_data = {k: str(v) for k, v in payload_data.items()}

        multicast_msg = self._build_multicast(
            [t.token for t in tokens], title, body, payload_data, image_url
        )

        response = self._messaging.send_each_for_multicast(
            multicast_msg, dry_run=settings.fcm_dry_run
        )
        invalidated = await self._handle_responses(db, tokens, response)

        return SendResult(
            success_count=response.success_count,
            failure_count=response.failure_count,
            invalidated_tokens=invalidated,
        )

    async def send_to_users(
        self,
        db: AsyncSession,
        user_ids: list[UUID],
        *,
        title: str,
        body: str,
        category: NotificationCategory,
        data: Optional[dict[str, Any]] = None,
        image_url: Optional[str] = None,
    ) -> SendResult:
        totals = SendResult(success_count=0, failure_count=0, invalidated_tokens=0)
        for user_id in user_ids:
            result = await self.send_to_user(
                db, user_id,
                title=title, body=body, category=category,
                data=data, image_url=image_url,
            )
            totals = SendResult(
                success_count=totals.success_count + result.success_count,
                failure_count=totals.failure_count + result.failure_count,
                invalidated_tokens=totals.invalidated_tokens + result.invalidated_tokens,
            )
        return totals

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _build_multicast(
        self,
        token_strings: list[str],
        title: str,
        body: str,
        data: dict[str, str],
        image_url: Optional[str],
    ) -> Any:
        messaging = self._messaging
        return messaging.MulticastMessage(
            tokens=token_strings,
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image_url,
            ),
            data=data,
            android=messaging.AndroidConfig(priority="high"),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default", content_available=True),
                )
            ),
        )

    async def _handle_responses(
        self,
        db: AsyncSession,
        tokens: list[DeviceToken],
        response: Any,
    ) -> int:
        _invalid_codes = {
            "UNREGISTERED",
            "INVALID_ARGUMENT",
            "registration-token-not-registered",
        }
        invalidated = 0
        needs_commit = False

        for token_row, send_response in zip(tokens, response.responses):
            if not send_response.success and send_response.exception:
                code = getattr(send_response.exception, "code", None) or ""
                if any(c in str(code) for c in _invalid_codes):
                    token_row.is_active = False
                    invalidated += 1
                    needs_commit = True

        if needs_commit:
            await db.commit()

        return invalidated


notification_service = NotificationService()
