from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from typing import List
from pydantic import BaseModel

from app.core.database.database import get_db
from app.models.user_model import User, UserProgress, LanguageChoice, LevelChoice
from password.common.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/home", tags=["home"])


# ─── Response Models ──────────────────────────────────────────────────────────

class DailyGoalResponse(BaseModel):
    completed: int
    target: int = 5  # Daily goal: 5 lessons/quizzes
    percentage: float


class ContinueLessonResponse(BaseModel):
    topic: str
    title: str  # Human-readable title
    language: str
    level: str
    progress_percentage: float
    emoji: str


class StatCardResponse(BaseModel):
    lessons_completed: int
    quiz_accuracy: float  # percentage
    total_xp: int


class TodayLessonResponse(BaseModel):
    id: str  # topic id
    emoji: str
    title: str
    subtitle: str
    duration_minutes: int
    is_completed: bool


class LeaderboardEntryResponse(BaseModel):
    rank: int
    name: str
    xp: int
    medal: str | None = None  # 🥇, 🥈, 🥉


class HomeDashboardResponse(BaseModel):
    user_name: str
    streak: int
    daily_goal: DailyGoalResponse
    continue_learning: ContinueLessonResponse | None
    stats: StatCardResponse
    today_lessons: List[TodayLessonResponse]
    leaderboard: List[LeaderboardEntryResponse]


# ─── Helper Functions ──────────────────────────────────────────────────────────

TOPIC_EMOJIS = {
    "greetings": "👋",
    "numbers": "🔢",
    "colors": "🎨",
    "family": "👨‍👩‍👧‍👦",
    "food": "🍲",
    "animals": "🦁",
    "body parts": "🫱",
    "days and time": "📅",
    "emotions": "😊",
    "market and shopping": "🛒",
    "travel": "✈️",
    "common verbs": "🏃",
    "forming sentences": "📝",
    "proverbs and culture": "🌍",
}

TOPIC_TITLES = {
    "greetings": "Greetings",
    "numbers": "Numbers 1-10",
    "colors": "Colors",
    "family": "Family Members",
    "food": "Food & Drinks",
    "animals": "Animals",
    "body parts": "Body Parts",
    "days and time": "Days & Time",
    "emotions": "Emotions",
    "market and shopping": "Market & Shopping",
    "travel": "Travel Phrases",
    "common verbs": "Common Verbs",
    "forming sentences": "Forming Sentences",
    "proverbs and culture": "Proverbs & Culture",
}

LEARNING_PATH = [
    "greetings", "numbers", "colors", "family", "food",
    "animals", "body parts", "days and time", "emotions",
    "market and shopping", "travel", "common verbs",
    "forming sentences", "proverbs and culture",
]

TOPIC_DURATIONS = {
    "greetings": 5, "numbers": 8, "colors": 6, "family": 7,
    "food": 8, "animals": 7, "body parts": 6, "days and time": 8,
    "emotions": 5, "market and shopping": 10, "travel": 9,
    "common verbs": 8, "forming sentences": 10, "proverbs and culture": 12,
}


async def get_today_completed_count(user_id: str, db: AsyncSession) -> int:
    """Count lessons completed today."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(UserProgress.id))
        .where(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.completed == True,
                UserProgress.completed_at >= today_start
            )
        )
    )
    return result.scalar() or 0


async def get_continue_learning(user: User, db: AsyncSession) -> ContinueLessonResponse | None:
    """Find the first incomplete topic in the learning path."""
    # Get all completed topics for user's selected language
    result = await db.execute(
        select(UserProgress.topic)
        .where(
            and_(
                UserProgress.user_id == user.id,
                UserProgress.language == user.selected_language,
                UserProgress.completed == True
            )
        )
    )
    completed_topics = set(result.scalars().all())
    
    # Find first incomplete topic
    next_topic = next(
        (t for t in LEARNING_PATH if t not in completed_topics),
        None
    )
    
    if not next_topic:
        return None
    
    # Calculate progress (rough estimate based on position)
    current_index = LEARNING_PATH.index(next_topic)
    progress = (current_index / len(LEARNING_PATH)) * 100
    
    return ContinueLessonResponse(
        topic=next_topic,
        title=TOPIC_TITLES.get(next_topic, next_topic.title()),
        language=user.selected_language.value if user.selected_language else "Igbo",
        level=user.level.value if user.level else "beginner",
        progress_percentage=min(progress, 100),
        emoji=TOPIC_EMOJIS.get(next_topic, "📚")
    )


async def get_stats(user: User, db: AsyncSession) -> StatCardResponse:
    """Calculate user statistics."""
    # Total completed lessons
    completed_result = await db.execute(
        select(func.count(UserProgress.id))
        .where(
            and_(
                UserProgress.user_id == user.id,
                UserProgress.completed == True
            )
        )
    )
    lessons_completed = completed_result.scalar() or 0
    
    # Quiz accuracy
    accuracy_result = await db.execute(
        select(func.avg(UserProgress.score))
        .where(
            and_(
                UserProgress.user_id == user.id,
                UserProgress.attempts > 0
            )
        )
    )
    avg_score = accuracy_result.scalar() or 0
    quiz_accuracy = min(avg_score, 100)  # Score is already percentage
    
    return StatCardResponse(
        lessons_completed=lessons_completed,
        quiz_accuracy=round(quiz_accuracy, 1),
        total_xp=user.total_xp
    )


async def get_today_lessons(user: User, db: AsyncSession) -> List[TodayLessonResponse]:
    """Get 3 recommended lessons for today."""
    # Get completed topics
    result = await db.execute(
        select(UserProgress.topic)
        .where(
            and_(
                UserProgress.user_id == user.id,
                UserProgress.language == user.selected_language,
                UserProgress.completed == True
            )
        )
    )
    completed_topics = set(result.scalars().all())
    
    # Get next 3 incomplete topics
    today_lessons = []
    for topic in LEARNING_PATH:
        if topic not in completed_topics and len(today_lessons) < 3:
            today_lessons.append(
                TodayLessonResponse(
                    id=topic,
                    emoji=TOPIC_EMOJIS.get(topic, "📚"),
                    title=TOPIC_TITLES.get(topic, topic.title()),
                    subtitle=f"{user.selected_language.value if user.selected_language else 'Igbo'} · {user.level.value if user.level else 'Beginner'}",
                    duration_minutes=TOPIC_DURATIONS.get(topic, 5),
                    is_completed=False
                )
            )
    
    return today_lessons


async def get_leaderboard(db: AsyncSession, limit: int = 3) -> List[LeaderboardEntryResponse]:
    """Get top users by XP earned this week."""
    week_start = datetime.now(timezone.utc) - timedelta(days=7)
    
    # This is a simplified leaderboard - you might want to track weekly XP separately
    result = await db.execute(
        select(User.full_name, User.total_xp)
        .where(User.is_active == True)
        .order_by(User.total_xp.desc())
        .limit(limit)
    )
    
    leaders = []
    medals = ["🥇", "🥈", "🥉"]
    for idx, (name, xp) in enumerate(result.all()):
        leaders.append(
            LeaderboardEntryResponse(
                rank=idx + 1,
                name=name or "Learner",
                xp=xp,
                medal=medals[idx] if idx < 3 else None
            )
        )
    
    return leaders


# ─── Main Endpoint ─────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=HomeDashboardResponse)
async def get_home_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all data needed for the home screen in one request."""
    
    # Get daily goal progress
    today_completed = await get_today_completed_count(current_user.id, db)
    daily_goal = DailyGoalResponse(
        completed=today_completed,
        target=5,
        percentage=(today_completed / 5) * 100
    )
    
    # Get continue learning
    continue_learning = await get_continue_learning(current_user, db)
    
    # Get stats
    stats = await get_stats(current_user, db)
    
    # Get today's lessons
    today_lessons = await get_today_lessons(current_user, db)
    
    # Get leaderboard
    leaderboard = await get_leaderboard(db)
    
    return HomeDashboardResponse(
        user_name=current_user.full_name.split()[0],  # First name only
        streak=current_user.streak_count,
        daily_goal=daily_goal,
        continue_learning=continue_learning,
        stats=stats,
        today_lessons=today_lessons,
        leaderboard=leaderboard
    )