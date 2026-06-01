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
from app.services.lessons_service import TOPICS_METADATA

# Learning path derived from the canonical topic order in lessons_service.
# This ensures topic IDs here always match what gets stored in UserProgress.
LEARNING_PATH = list(TOPICS_METADATA.keys())


class HomeService:
    DAILY_GOAL_TARGET = 5

    async def get_home_dashboard(self, user: User, db: AsyncSession) -> HomeDashboardResponse:
        today_completed = await self._get_today_completed_count(str(user.id), db)
        daily_goal = DailyGoalResponse(
            completed=today_completed,
            target=self.DAILY_GOAL_TARGET,
            percentage=min((today_completed / self.DAILY_GOAL_TARGET) * 100, 100),
        )

        # One DB query shared by continue_learning and today_lessons
        fully_completed = await self._get_fully_completed_topics(user, db)
        continue_learning = self._build_continue_learning(user, fully_completed)
        today_lessons = self._build_today_lessons(user, fully_completed)

        stats = await self._get_stats(user, db)
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

    async def _get_fully_completed_topics(self, user: User, db: AsyncSession) -> set:
        """Returns topics where every subtopic has a completed=True record."""
        result = await db.execute(
            select(UserProgress.topic, func.count(UserProgress.id))
            .where(
                and_(
                    UserProgress.user_id == user.id,
                    UserProgress.language == user.selected_language,
                    UserProgress.completed == True,
                )
            )
            .group_by(UserProgress.topic)
        )
        completed_counts = {topic: count for topic, count in result.all()}

        fully_completed = set()
        for topic, count in completed_counts.items():
            expected = len(TOPICS_METADATA.get(topic, {}).get("subtopics", []))
            if expected > 0 and count >= expected:
                fully_completed.add(topic)
        return fully_completed

    def _build_continue_learning(self, user: User, fully_completed: set) -> ContinueLessonResponse | None:
        next_topic = next((t for t in LEARNING_PATH if t not in fully_completed), None)
        if not next_topic:
            return None

        current_index = LEARNING_PATH.index(next_topic)
        progress = (current_index / len(LEARNING_PATH)) * 100
        topic_meta = TOPICS_METADATA.get(next_topic, {})

        return ContinueLessonResponse(
            topic=next_topic,
            title=topic_meta.get("title", next_topic.replace("_", " ").title()),
            language=user.selected_language.value if user.selected_language else "Igbo",
            level=user.level.value if user.level else "beginner",
            progress_percentage=min(progress, 100),
            emoji=topic_meta.get("emoji", "📚"),
        )

    def _build_today_lessons(self, user: User, fully_completed: set) -> List[TodayLessonResponse]:
        today_lessons: List[TodayLessonResponse] = []
        for topic in LEARNING_PATH:
            if len(today_lessons) >= 3:
                break
            if topic in fully_completed:
                continue

            topic_meta = TOPICS_METADATA.get(topic, {})
            today_lessons.append(
                TodayLessonResponse(
                    id=topic,
                    emoji=topic_meta.get("emoji", "📚"),
                    title=topic_meta.get("title", topic.replace("_", " ").title()),
                    subtitle=f"{user.selected_language.value if user.selected_language else 'Igbo'} · {user.level.value if user.level else 'Beginner'}",
                    duration_minutes=topic_meta.get("duration_minutes", 5),
                    is_completed=False,
                )
            )
        return today_lessons

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
