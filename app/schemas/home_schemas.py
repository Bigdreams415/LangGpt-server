from typing import List

from pydantic import BaseModel


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
    medal: str | None = None  # top 3 marker


class HomeDashboardResponse(BaseModel):
    user_name: str
    streak: int
    daily_goal: DailyGoalResponse
    continue_learning: ContinueLessonResponse | None
    stats: StatCardResponse
    today_lessons: List[TodayLessonResponse]
    leaderboard: List[LeaderboardEntryResponse]
