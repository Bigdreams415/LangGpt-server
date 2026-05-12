from datetime import datetime, timezone
from typing import List

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User, UserProgress
from app.schemas.home_schemas import (
    ContinueLessonResponse,
    DailyGoalResponse,
    HomeDashboardResponse,
    LeaderboardEntryResponse,
    StatCardResponse,
    TodayLessonResponse,
)


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
    "greetings": 5,
    "numbers": 8,
    "colors": 6,
    "family": 7,
    "food": 8,
    "animals": 7,
    "body parts": 6,
    "days and time": 8,
    "emotions": 5,
    "market and shopping": 10,
    "travel": 9,
    "common verbs": 8,
    "forming sentences": 10,
    "proverbs and culture": 12,
}


class HomeService:
    DAILY_GOAL_TARGET = 5

    async def get_home_dashboard(self, user: User, db: AsyncSession) -> HomeDashboardResponse:
        today_completed = await self._get_today_completed_count(str(user.id), db)
        daily_goal = DailyGoalResponse(
            completed=today_completed,
            target=self.DAILY_GOAL_TARGET,
            percentage=(today_completed / self.DAILY_GOAL_TARGET) * 100,
        )

        continue_learning = await self._get_continue_learning(user, db)
        stats = await self._get_stats(user, db)
        today_lessons = await self._get_today_lessons(user, db)
        leaderboard = await self._get_leaderboard(db, language=user.selected_language)

        return HomeDashboardResponse(
            user_name=(user.full_name or "Learner").split()[0],
            streak=user.streak_count,
            daily_goal=daily_goal,
            continue_learning=continue_learning,
            stats=stats,
            today_lessons=today_lessons,
            leaderboard=leaderboard,
        )

    async def _get_today_completed_count(self, user_id: str, db: AsyncSession) -> int:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.count(UserProgress.id)).where(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.completed == True,
                    UserProgress.completed_at >= today_start,
                )
            )
        )
        return result.scalar() or 0

    async def _get_continue_learning(self, user: User, db: AsyncSession) -> ContinueLessonResponse | None:
        result = await db.execute(
            select(UserProgress.topic).where(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.language == user.selected_language,
                    UserProgress.completed == True,
                )
            )
        )
        completed_topics = set(result.scalars().all())

        next_topic = next((topic for topic in LEARNING_PATH if topic not in completed_topics), None)
        if not next_topic:
            return None

        current_index = LEARNING_PATH.index(next_topic)
        progress = (current_index / len(LEARNING_PATH)) * 100

        return ContinueLessonResponse(
            topic=next_topic,
            title=TOPIC_TITLES.get(next_topic, next_topic.title()),
            language=user.selected_language.value if user.selected_language else "Igbo",
            level=user.level.value if user.level else "beginner",
            progress_percentage=min(progress, 100),
            emoji=TOPIC_EMOJIS.get(next_topic, "📚"),
        )

    async def _get_stats(self, user: User, db: AsyncSession) -> StatCardResponse:
        completed_result = await db.execute(
            select(func.count(UserProgress.id)).where(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.completed == True,
                )
            )
        )
        lessons_completed = completed_result.scalar() or 0

        accuracy_result = await db.execute(
            select(func.avg(UserProgress.score)).where(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.attempts > 0,
                )
            )
        )
        avg_score = accuracy_result.scalar() or 0
        quiz_accuracy = min(avg_score, 100)

        return StatCardResponse(
            lessons_completed=lessons_completed,
            quiz_accuracy=round(quiz_accuracy, 1),
            total_xp=user.total_xp,
        )

    async def _get_today_lessons(self, user: User, db: AsyncSession) -> List[TodayLessonResponse]:
        result = await db.execute(
            select(UserProgress.topic).where(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.language == user.selected_language,
                    UserProgress.completed == True,
                )
            )
        )
        completed_topics = set(result.scalars().all())

        today_lessons: List[TodayLessonResponse] = []
        for topic in LEARNING_PATH:
            if topic in completed_topics or len(today_lessons) >= 3:
                continue

            today_lessons.append(
                TodayLessonResponse(
                    id=topic,
                    emoji=TOPIC_EMOJIS.get(topic, "📚"),
                    title=TOPIC_TITLES.get(topic, topic.title()),
                    subtitle=f"{user.selected_language.value if user.selected_language else 'Igbo'} · {user.level.value if user.level else 'Beginner'}",
                    duration_minutes=TOPIC_DURATIONS.get(topic, 5),
                    is_completed=False,
                )
            )

        return today_lessons

    async def _get_leaderboard(self, db: AsyncSession, language=None, limit: int = 5) -> List[LeaderboardEntryResponse]:
        query = select(User.full_name, User.total_xp).where(User.is_active == True)
        if language is not None:
            query = query.where(User.selected_language == language)
        result = await db.execute(
            query.order_by(User.total_xp.desc()).limit(limit)
        )

        medals = ["🥇", "🥈", "🥉"]
        leaders: List[LeaderboardEntryResponse] = []
        for idx, (name, xp) in enumerate(result.all()):
            leaders.append(
                LeaderboardEntryResponse(
                    rank=idx + 1,
                    name=name or "Learner",
                    xp=xp,
                    medal=medals[idx] if idx < len(medals) else None,
                )
            )

        return leaders


home_service = HomeService()
