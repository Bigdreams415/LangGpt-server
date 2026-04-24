from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config.settings import settings
from app.core.database.database import init_db, close_db
from app.core.database.redis import inits_redis, close_redis
from app.routers import lessons, quiz, conversation, progress, auth, avatar
from app.routers.home import router as home


# Ensure static directories exist at startup
STATIC_VIDEOS_DIR = Path(__file__).resolve().parent.parent / "static" / "videos"
STATIC_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    await init_redis()
    await init_db()
    yield
    await close_redis()
    await close_db()


app = FastAPI(
    title="LangGpt API",
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


@app.get("/")
def root():
    return {
        "message": "LangGpt API is running!",
        "supported_languages": ["Igbo", "Yoruba", "Hausa"],
        "docs": "/docs",
    }