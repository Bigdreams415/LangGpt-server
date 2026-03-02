from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config.settings import settings
from app.core.database.database import init_db, close_db
from app.core.database.redis import init_redis, close_redis
from app.routers import lessons, quiz, conversation, progress, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    # Startup
    await init_redis()
    await init_db()
    yield
    # Shutdown
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

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
app.include_router(conversation.router, prefix="/conversation", tags=["Conversation"])
app.include_router(progress.router, prefix="/progress", tags=["Progress"])


@app.get("/")
def root():
    return {
        "message": "LangGpt API is running!",
        "supported_languages": ["Igbo", "Yoruba", "Hausa"],
        "docs": "/docs",
    }