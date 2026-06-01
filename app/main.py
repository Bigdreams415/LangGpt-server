from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config.settings import settings
from app.core.database.database import init_db, close_db
from app.core.database.redis import init_redis, close_redis

logger = logging.getLogger(__name__)
from app.routers import lessons, quiz, conversation, progress, auth, avatar, notifications, user_routes
from app.routers.home import router as home
from app.services.notification_service import notification_service


# Ensure static directories exist at startup
STATIC_VIDEOS_DIR = Path(__file__).resolve().parent.parent / "static" / "videos"
STATIC_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    await init_redis()
    await init_db()
    notification_service.initialize(settings.firebase_credentials_path)
    yield
    await close_redis()
    await close_db()


app = FastAPI(
    title="KinSpeak API",
    description="Language learning backend for Igbo, Yoruba, and Hausa",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again later."},
    )

# Serve generated avatar videos as static files
# Accessible at: /static/videos/<filename>.mp4
app.mount(
    "/static/videos",
    StaticFiles(directory=str(STATIC_VIDEOS_DIR)),
    name="videos",
)

# Routers
app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["Auth"])
app.include_router(lessons.router,      prefix="/api/v1/lessons",      tags=["Lessons"])
app.include_router(quiz.router,         prefix="/api/v1/quiz",         tags=["Quiz"])
app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["Conversation"])
app.include_router(progress.router,     prefix="/api/v1/progress",     tags=["Progress"])
app.include_router(avatar.router,       prefix="/api/v1/avatar",       tags=["Avatar"])
app.include_router(home,                prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(user_routes.router,   prefix="/api/v1/users",         tags=["Users"])


@app.get("/")
def root():
    return {
        "message": "KinSpeak API is running!",
        "supported_languages": ["Igbo", "Yoruba", "Hausa"],
        "docs": "/docs",
    }