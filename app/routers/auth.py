from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database.database import get_db
from app.core.database.redis import get_redis
from app.services.auth_service import auth_service
from app.schemas.auth_schemas import (
    SignupRequest, LoginRequest, GoogleAuthRequest,
    TokenResponse, AuthResponse, RefreshTokenRequest,
    MessageResponse,
)
from password.common.dependencies import (
    get_current_user, get_token_from_request
)
from app.models import User
from app.schemas.auth_schemas import UserResponse


router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new account with email/password. Returns user data + JWT tokens.",
)
async def signup(
    data: SignupRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await auth_service.signup(data, db, redis)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email or username + password",
    description="Accepts email address OR username in the 'identifier' field.",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await auth_service.login(data, db, redis)


@router.post(
    "/google",
    response_model=AuthResponse,
    summary="Sign in or sign up with Google",
    description=(
        "Flutter sends the Google ID token after on-device Google Sign-In. "
        "If the account doesn't exist, it's created automatically. "
        "Check `is_new_user` in response to route to onboarding."
    ),
)
async def google_auth(
    data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await auth_service.google_auth(data, db, redis)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Send the refresh token to get a new access token. Old refresh token is invalidated (rotation).",
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    return await auth_service.refresh_tokens(data.refresh_token, db, redis)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="Invalidates the current access token and deletes the refresh token.",
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    token = get_token_from_request(request)
    await auth_service.logout(str(current_user.id), token, redis)
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    summary="Get current user",
    description="Returns the profile of the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)