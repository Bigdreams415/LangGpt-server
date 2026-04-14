from typing import List, Optional
from datetime import datetime
from functools import lru_cache

from app.schemas.lessons_schemas import (
    LessonTopicResponse,
    LessonsListResponse,
    LessonDetailResponse,
)


# Topic metadata constants
TOPICS_METADATA = {
    "greetings": {
        "title": "Greetings",
        "emoji": "👋",
        "description": "Learn essential greetings and introductions",
        "duration_minutes": 5,
        "level": "beginner",
    },
    "numbers": {
        "title": "Numbers 1-10",
        "emoji": "🔢",
        "description": "Master counting and basic numbers",
        "duration_minutes": 8,
        "level": "beginner",
    },
    "colors": {
        "title": "Colors",
        "emoji": "🎨",
        "description": "Learn color names and descriptions",
        "duration_minutes": 6,
        "level": "beginner",
    },
    "family": {
        "title": "Family Members",
        "emoji": "👨‍👩‍👧‍👦",
        "description": "Names for family relations",
        "duration_minutes": 7,
        "level": "beginner",
    },
    "food": {
        "title": "Food & Drinks",
        "emoji": "🍲",
        "description": "Common foods and dining phrases",
        "duration_minutes": 8,
        "level": "beginner",
    },
    "animals": {
        "title": "Animals",
        "emoji": "🦁",
        "description": "Names of common animals",
        "duration_minutes": 7,
        "level": "beginner",
    },
    "body parts": {
        "title": "Body Parts",
        "emoji": "🫱",
        "description": "Learn parts of the body",
        "duration_minutes": 6,
        "level": "intermediate",
    },
    "days and time": {
        "title": "Days & Time",
        "emoji": "📅",
        "description": "Days of week and telling time",
        "duration_minutes": 8,
        "level": "intermediate",
    },
    "emotions": {
        "title": "Emotions",
        "emoji": "😊",
        "description": "Express feelings and emotions",
        "duration_minutes": 5,
        "level": "intermediate",
    },
    "market and shopping": {
        "title": "Market & Shopping",
        "emoji": "🛒",
        "description": "Buying and selling phrases",
        "duration_minutes": 10,
        "level": "intermediate",
    },
    "travel": {
        "title": "Travel Phrases",
        "emoji": "✈️",
        "description": "Essential phrases for traveling",
        "duration_minutes": 9,
        "level": "advanced",
    },
    "common verbs": {
        "title": "Common Verbs",
        "emoji": "🏃",
        "description": "Most frequently used verbs",
        "duration_minutes": 8,
        "level": "advanced",
    },
    "forming sentences": {
        "title": "Forming Sentences",
        "emoji": "📝",
        "description": "Basic sentence structure",
        "duration_minutes": 10,
        "level": "advanced",
    },
    "proverbs and culture": {
        "title": "Proverbs & Culture",
        "emoji": "🌍",
        "description": "Cultural insights and proverbs",
        "duration_minutes": 12,
        "level": "advanced",
    },
}

VALID_LANGUAGES = ["Igbo", "Yoruba", "Hausa"]


class LessonsService:
    
    def get_lessons_list(
        self,
        language: str,
        level: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> LessonsListResponse:
        """Get paginated list of available lessons for a language."""
        
        if language not in VALID_LANGUAGES:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Must be one of: {', '.join(VALID_LANGUAGES)}"
            )
        
        # Build topics list
        all_topics = []
        for topic_id, metadata in TOPICS_METADATA.items():
            # Filter by level if specified
            if level and level.lower() != metadata["level"]:
                continue
            
            all_topics.append(
                LessonTopicResponse(
                    id=topic_id,
                    title=metadata["title"],
                    emoji=metadata["emoji"],
                    description=metadata["description"],
                    duration_minutes=metadata["duration_minutes"],
                    level=metadata["level"],
                    is_completed=False,
                )
            )
        
        total = len(all_topics)
        paginated_topics = all_topics[offset:offset + limit]
        
        return LessonsListResponse(
            topics=paginated_topics,
            total=total,
            language=language,
        )
    
    def get_lesson_detail(self, language: str, topic_id: str) -> LessonDetailResponse:
        """Get detailed lesson content for a specific topic."""
        
        if language not in VALID_LANGUAGES:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Must be one of: {', '.join(VALID_LANGUAGES)}"
            )
        
        if topic_id not in TOPICS_METADATA:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Topic not found")
        
        metadata = TOPICS_METADATA[topic_id]
        
        return LessonDetailResponse(
            id=topic_id,
            language=language,
            title=metadata["title"],
            emoji=metadata["emoji"],
            level=metadata["level"],
            content={
                "vocabulary": [
                    {"word": f"{metadata['title']} word 1", "translation": "Translation 1"},
                    {"word": f"{metadata['title']} word 2", "translation": "Translation 2"},
                ],
                "phrases": [
                    {"phrase": f"Example phrase 1", "translation": "Translation 1"},
                    {"phrase": f"Example phrase 2", "translation": "Translation 2"},
                ],
            },
        )


lessons_service = LessonsService()