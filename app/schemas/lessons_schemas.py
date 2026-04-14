from typing import List, Optional
from pydantic import BaseModel


class LessonTopicResponse(BaseModel):
    id: str
    title: str
    emoji: str
    description: str
    duration_minutes: int
    is_completed: bool = False
    level: str


class LessonsListResponse(BaseModel):
    topics: List[LessonTopicResponse]
    total: int
    language: str


class LessonDetailResponse(BaseModel):
    id: str
    language: str
    title: str
    emoji: str
    level: str
    content: dict