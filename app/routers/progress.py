from fastapi import APIRouter, HTTPException
from app.models.schemas import ProgressUpdateRequest, ProgressResponse, LessonTopic

router = APIRouter()

# Simple in-memory store — replace with PostgreSQL/Supabase when ready
_progress_store: dict = {}

# Topic order defines the learning path (beginner → advanced)
LEARNING_PATH = [
    "greetings", "numbers", "colors", "family", "food",
    "animals", "body parts", "days and time", "emotions",
    "market and shopping", "travel", "common verbs",
    "forming sentences", "proverbs and culture",
]


@router.post("/update", response_model=ProgressResponse)
async def update_progress(request: ProgressUpdateRequest):
    """Record a completed lesson/quiz score for a user."""
    key = f"{request.user_id}:{request.language}"
    if key not in _progress_store:
        _progress_store[key] = {
            "completed_topics": [],
            "scores": {},
            "current_level": "beginner",
            "total_score": 0,
        }

    record = _progress_store[key]
    topic_val = request.topic.value

    if topic_val not in record["completed_topics"]:
        record["completed_topics"].append(topic_val)
    record["scores"][topic_val] = request.score
    record["total_score"] = sum(record["scores"].values())
    record["current_level"] = request.level.value

    # Recommend next topic not yet completed
    next_topic = next(
        (t for t in LEARNING_PATH if t not in record["completed_topics"]),
        "proverbs and culture",  # Final topic if all done
    )

    return ProgressResponse(
        user_id=request.user_id,
        language=request.language.value,
        completed_topics=record["completed_topics"],
        current_level=record["current_level"],
        total_score=record["total_score"],
        next_recommended_topic=next_topic,
    )


@router.get("/{user_id}/{language}", response_model=ProgressResponse)
async def get_progress(user_id: str, language: str):
    """Get a user's progress for a specific language."""
    key = f"{user_id}:{language}"
    if key not in _progress_store:
        # Return empty progress for new users
        next_topic = LEARNING_PATH[0]
        return ProgressResponse(
            user_id=user_id,
            language=language,
            completed_topics=[],
            current_level="beginner",
            total_score=0,
            next_recommended_topic=next_topic,
        )

    record = _progress_store[key]
    next_topic = next(
        (t for t in LEARNING_PATH if t not in record["completed_topics"]),
        "proverbs and culture",
    )

    return ProgressResponse(
        user_id=user_id,
        language=language,
        completed_topics=record["completed_topics"],
        current_level=record["current_level"],
        total_score=record["total_score"],
        next_recommended_topic=next_topic,
    )