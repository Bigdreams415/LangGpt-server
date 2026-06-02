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


class LessonUnit(str, Enum):
    """
    The 16 learning units. Each unit contains multiple ordered subtopics.
        Unit (e.g. greetings) → Subtopic (e.g. 'Basic hello & goodbye')
    """
    foundations         = "foundations"
    greetings           = "greetings"
    numbers             = "numbers"
    colors_descriptions = "colors_descriptions"
    family              = "family"
    body                = "body"
    food                = "food"
    home                = "home"
    days_time           = "days_time"
    animals_nature      = "animals_nature"
    emotions            = "emotions"
    market              = "market"
    travel              = "travel"
    verbs               = "verbs"
    sentences           = "sentences"
    culture             = "culture"



# Lesson models
class LessonRequest(BaseModel):
    language: Language
    level: Level = Level.beginner
    unit: LessonUnit = LessonUnit.greetings
    subtopic_index: int = 0          # 0-based index into the unit's subtopics list
    subtopic_name: Optional[str] = None   # Optional override — takes priority over index


class VocabItem(BaseModel):
    word: str
    translation: str
    pronunciation: str
    example_sentence: str
    sentence_translation: str


class LessonResponse(BaseModel):
    language: str
    level: str
    unit: str
    subtopic: str                       # Name of the specific subtopic taught
    subtopic_index: int                 # Position within the unit (0-based)
    total_subtopics: int                # Total subtopics in this unit
    introduction: str
    vocabulary: List[VocabItem]
    cultural_note: str
    tip: str
    next_subtopic: Optional[str] = None # Name of the next subtopic (None if last)


# Quiz models
class QuizRequest(BaseModel):
    language: Language
    level: Level = Level.beginner
    unit: LessonUnit = LessonUnit.greetings
    subtopic_index: int = 0
    subtopic_name: Optional[str] = None
    num_questions: int = 5


class QuizQuestion(BaseModel):
    question: str
    options: List[str]       # 4 options (A, B, C, D)
    correct_answer: str      # The correct option text
    explanation: str


class QuizResponse(BaseModel):
    language: str
    unit: str
    subtopic: str
    questions: List[QuizQuestion]


# Answer checking
class CheckAnswerRequest(BaseModel):
    language: Language
    question: str
    user_answer: str
    correct_answer: str


class CheckAnswerResponse(BaseModel):
    is_correct: bool
    feedback: str
    encouragement: str


# Conversation models
class ConversationRequest(BaseModel):
    language: Language
    level: Level = Level.beginner
    unit: LessonUnit = LessonUnit.greetings
    subtopic_index: int = 0
    subtopic_name: Optional[str] = None
    user_message: str
    conversation_history: Optional[List[dict]] = []  # [{role, content}]


class ConversationResponse(BaseModel):
    reply: str
    translation: str
    corrections: Optional[str] = None
    vocabulary_used: Optional[List[str]] = []



# Translation models

class TranslationRequest(BaseModel):
    text: str
    from_language: str      # "English" or one of the 3 languages
    to_language: Language


class TranslationResponse(BaseModel):
    original: str
    translation: str
    pronunciation: str
    breakdown: Optional[str] = None  # Word-by-word explanation

    @field_validator("breakdown", mode="before")
    @classmethod
    def coerce_breakdown_to_str(cls, v):
        if isinstance(v, dict):
            return " | ".join(f"{k}: {val}" for k, val in v.items())
        return v


# Progress models
class SubtopicProgress(BaseModel):
    unit: str
    subtopic_name: str
    subtopic_index: int
    score: int                  # 0-100
    completed: bool


class ProgressUpdateRequest(BaseModel):
    user_id: str
    language: Language
    unit: LessonUnit
    subtopic_index: int
    subtopic_name: str
    score: int                  # 0-100
    level: Level


class ProgressResponse(BaseModel):
    user_id: str
    language: str
    completed_units: List[str]
    unlocked_units: List[str] = []      # Units the learner is allowed to open
    completed_subtopics: List[SubtopicProgress]
    current_unit: str
    current_subtopic: str
    current_level: str
    total_score: int
    next_recommended_unit: str
    next_recommended_subtopic: str
    overall_progress_percent: float     # 0.0–100.0
    streak_count: int = 0
    total_xp: int = 0