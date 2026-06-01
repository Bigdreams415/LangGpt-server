from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification_model import DevicePlatform


class NotificationCategory(str, Enum):
    DAILY_REMINDERS = "daily_reminders"
    STREAK_REMINDERS = "streak_reminders"
    LESSON_UPDATES = "lesson_updates"
    ACHIEVEMENTS = "achievements"
    NEW_CONTENT = "new_content"
    MARKETING = "marketing"


class NotificationPreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    push_enabled: bool
    daily_reminders: bool
    streak_reminders: bool
    lesson_updates: bool
    achievements: bool
    new_content: bool
    marketing: bool


class NotificationPreferencesUpdate(BaseModel):
    push_enabled: Optional[bool] = None
    daily_reminders: Optional[bool] = None
    streak_reminders: Optional[bool] = None
    lesson_updates: Optional[bool] = None
    achievements: Optional[bool] = None
    new_content: Optional[bool] = None
    marketing: Optional[bool] = None


class DeviceTokenRegister(BaseModel):
    token: str = Field(min_length=10)
    platform: DevicePlatform
    device_info: Optional[str] = None


class DeviceTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    platform: DevicePlatform
    is_active: bool
    last_used_at: datetime


class TestNotificationRequest(BaseModel):
    title: str = "KinSpeak"
    body: str = "Test push notification from backend"
    route: Optional[str] = "/notifications"


class SendResult(BaseModel):
    success_count: int
    failure_count: int
    invalidated_tokens: int
