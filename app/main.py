from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import lessons, quiz, conversation, progress

app = FastAPI(
    title="LangGpt API",
    description="Language learning backend for Igbo, Yoruba, and Hausa",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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