from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database.database import get_db
from app.schemas.auth_schemas import (
    UserResponse, UpdateProfileRequest,
    ChangePasswordRequest, MessageResponse
)
from password.common.dependencies.auth_dependencies import get_current_user
from password.dependency.exceptions import AuthException
from app.core.security.jwt import verify_password, hash_password
from app.models.user_model import User, LanguageChoice, LevelChoice

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get my profile",
)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update my profile",
)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check username uniqueness if being changed
    if data.username and data.username.lower() != current_user.username:
        existing = await db.scalar(
            select(User).where(User.username == data.username.lower())
        )
        if existing:
            raise AuthException.username_taken()
        current_user.username = data.username.lower()

    if data.full_name:
        current_user.full_name = data.full_name
    if data.date_of_birth is not None:
        current_user.date_of_birth = data.date_of_birth
    if data.country is not None:
        current_user.country = data.country
    if data.selected_language is not None:
        try:
            current_user.selected_language = LanguageChoice(data.selected_language)
        except ValueError:
            pass
    if data.level is not None:
        try:
            current_user.level = LevelChoice(data.level)
        except ValueError:
            pass

    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="Change password",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.hashed_password:
        raise AuthException.not_authorized()  # Google-only account

    if not verify_password(data.current_password, current_user.hashed_password):
        raise AuthException.invalid_credentials()

    current_user.hashed_password = hash_password(data.new_password)
    await db.commit()

    return MessageResponse(message="Password changed successfully")


@router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete my account",
)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.is_active = False  # Soft delete
    await db.commit()
    return MessageResponse(message="Account deactivated successfully")