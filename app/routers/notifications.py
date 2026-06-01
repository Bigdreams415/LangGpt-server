from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import settings
from app.core.database.database import get_db
from app.models.user_model import User
from app.schemas.notification_schemas import (
    DeviceTokenRegister,
    DeviceTokenResponse,
    NotificationCategory,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    SendResult,
    TestNotificationRequest,
)
from app.services.notification_service import notification_service
from password.common.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    summary="Get notification preferences",
    description="Returns the current user's notification preferences. Creates defaults on first call.",
)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_service.get_or_create_preferences(db, current_user)


@router.put(
    "/preferences",
    response_model=NotificationPreferencesResponse,
    summary="Update notification preferences",
    description="Updates only the fields provided in the request body.",
)
async def update_preferences(
    payload: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_service.update_preferences(db, current_user, payload)


@router.post(
    "/device-token",
    response_model=DeviceTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register device token",
    description="Registers an FCM device token for push notifications. Upserts by token value.",
)
async def register_device_token(
    payload: DeviceTokenRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_service.register_device_token(
        db,
        current_user,
        payload.token,
        payload.platform,
        payload.device_info,
    )


@router.delete(
    "/device-token",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister device token",
    description="Soft-deletes the device token so the user no longer receives pushes on this device.",
)
async def unregister_device_token(
    token: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await notification_service.unregister_device_token(db, current_user, token)


@router.post(
    "/test",
    response_model=SendResult,
    summary="Send a test push notification",
    description="Available in debug mode or to superusers. Fires a real push to the current user's devices.",
)
async def test_push(
    payload: TestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not (settings.debug or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoint is only available in debug mode",
        )
    return await notification_service.send_to_user(
        db,
        current_user.id,
        title=payload.title,
        body=payload.body,
        category=NotificationCategory.DAILY_REMINDERS,
        data={"route": payload.route or "/notifications", "test": "1"},
    )
