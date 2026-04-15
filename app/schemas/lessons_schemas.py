from pydantic import BaseModel
from typing import List, Optional, Any


class SubtopicMeta(BaseModel):
    """Metadata for a single subtopic within a unit."""
    index: int
    name: str
    description: str
    duration_minutes: int
    is_completed: bool = False


class LessonUnitResponse(BaseModel):
    """
    Summary card for a lesson unit — returned in paginated list views.
    Does NOT include the full subtopic list (use LessonDetailResponse for that).
    """
    id: str
    title: str
    emoji: str
    description: str
    duration_minutes: int
    level: str
    subtopic_count: int         # How many subtopics the unit has
    is_completed: bool = False


class LessonsListResponse(BaseModel):
    """Paginated list of lesson units for a given language."""
    topics: List[LessonUnitResponse]
    total: int
    language: str


class LessonDetailResponse(BaseModel):
    """
    Full detail for a single lesson unit, including all subtopics.
    The `content` field is intentionally left empty here — actual lesson
    content (vocabulary, cultural notes, etc.) is AI-generated at
    POST /lessons/ with a specific subtopic_index.
    """
    id: str
    language: str
    title: str
    emoji: str
    level: str
    subtopics: List[dict]       # List of {name, description, duration_minutes}
    content: Any = None