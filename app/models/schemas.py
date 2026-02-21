from pydantic import BaseModel, field_validator
from typing import Optional, List
from enum import Enum


class Language(str, Enum):
    igbo = "Igbo"
    yoruba = "Yoruba"
    hausa = "Hausa"


class Level(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LessonTopic(str, Enum):
    greetings = "greetings"
    numbers = "numbers"
    colors = "colors"
    family = "family"
    food = "food"
    animals = "animals"
    body_parts = "body parts"
    days_and_time = "days and time"
    travel = "travel"
    market = "market and shopping"
    emotions = "emotions"
    verbs = "common verbs"
    sentences = "forming sentences"
    proverbs = "proverbs and culture"


# ─── Lesson Models ────────────────────────────────────────────────────────────

class LessonRequest(BaseModel):
    language: Language
    level: Level = Level.beginner
    topic: LessonTopic = LessonTopic.greetings

class VocabItem(BaseModel):
    word: str
    translation: str
    pronunciation: str
    example_sentence: str
    sentence_translation: str

class LessonResponse(BaseModel):
    language: str
    level: str
    topic: str
    introduction: str
    vocabulary: List[VocabItem]
    cultural_note: str
    tip: str


# ─── Quiz Models ──────────────────────────────────────────────────────────────

class QuizRequest(BaseModel):
    language: Language
    level: Level = Level.beginner
    topic: LessonTopic = LessonTopic.greetings
    num_questions: int = 5

class QuizQuestion(BaseModel):
    question: str
    options: List[str]          # 4 options (A, B, C, D)
    correct_answer: str         # The correct option text
    explanation: str

class QuizResponse(BaseModel):
    language: str
    topic: str
    questions: List[QuizQuestion]


# ─── Answer Checking ──────────────────────────────────────────────────────────

class CheckAnswerRequest(BaseModel):
    language: Language
    question: str
    user_answer: str
    correct_answer: str

class CheckAnswerResponse(BaseModel):
    is_correct: bool
    feedback: str
    encouragement: str


# ─── Conversation Models ──────────────────────────────────────────────────────

class ConversationRequest(BaseModel):
    language: Language
    level: Level = Level.beginner
    topic: LessonTopic = LessonTopic.greetings
    user_message: str
    conversation_history: Optional[List[dict]] = []  # [{role, content}]

class ConversationResponse(BaseModel):
    reply: str
    translation: str
    corrections: Optional[str] = None
    vocabulary_used: Optional[List[str]] = []


# ─── Translation Models ───────────────────────────────────────────────────────

class TranslationRequest(BaseModel):
    text: str
    from_language: str   # "English" or one of the 3 languages
    to_language: Language

class TranslationResponse(BaseModel):
    original: str
    translation: str
    pronunciation: str
    breakdown: Optional[str] = None  # Word-by-word explanation

    @field_validator("breakdown", mode="before")
    @classmethod
    def coerce_breakdown_to_str(cls, v):
        # Gemini sometimes returns a dict — convert it to a readable string
        if isinstance(v, dict):
            return " | ".join(f"{k}: {val}" for k, val in v.items())
        return v


# ─── Progress Models ──────────────────────────────────────────────────────────

class ProgressUpdateRequest(BaseModel):
    user_id: str
    language: Language
    topic: LessonTopic
    score: int          # 0-100
    level: Level

class ProgressResponse(BaseModel):
    user_id: str
    language: str
    completed_topics: List[str]
    current_level: str
    total_score: int
    next_recommended_topic: str