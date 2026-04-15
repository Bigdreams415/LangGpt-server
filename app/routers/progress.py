from fastapi import APIRouter

from app.models.schemas import (
    LessonUnit,
    ProgressResponse,
    ProgressUpdateRequest,
    SubtopicProgress,
)

router = APIRouter()

# Simple in-memory store — replace with PostgreSQL/Supabase when ready
_progress_store: dict = {}

# Unit order defines the learning path (beginner → advanced)
LEARNING_PATH = [unit.value for unit in LessonUnit]


@router.post("/update", response_model=ProgressResponse)
async def update_progress(request: ProgressUpdateRequest):
    """Record a completed lesson/quiz score for a user."""
    key = f"{request.user_id}:{request.language.value}"
    if key not in _progress_store:
        _progress_store[key] = {
            "completed_units": [],
            "completed_subtopics": {},
            "current_level": "beginner",
            "total_score": 0,
        }

    record = _progress_store[key]
    unit_val = request.unit.value
    subtopic_key = f"{unit_val}:{request.subtopic_index}"

    if unit_val not in record["completed_units"]:
        record["completed_units"].append(unit_val)

    record["completed_subtopics"][subtopic_key] = {
        "unit": unit_val,
        "subtopic_name": request.subtopic_name,
        "subtopic_index": request.subtopic_index,
        "score": request.score,
        "completed": True,
    }

    record["total_score"] = sum(
        item["score"] for item in record["completed_subtopics"].values()
    )
    record["current_level"] = request.level.value

    # Recommend next unit not yet completed
    next_unit = next(
        (u for u in LEARNING_PATH if u not in record["completed_units"]),
        LEARNING_PATH[-1],
    )

    completed_subtopics = [
        SubtopicProgress(**item) for item in record["completed_subtopics"].values()
    ]

    overall_progress_percent = (len(record["completed_units"]) / len(LEARNING_PATH)) * 100

    return ProgressResponse(
        user_id=request.user_id,
        language=request.language.value,
        completed_units=record["completed_units"],
        completed_subtopics=completed_subtopics,
        current_unit=unit_val,
        current_subtopic=request.subtopic_name,
        current_level=record["current_level"],
        total_score=record["total_score"],
        next_recommended_unit=next_unit,
        next_recommended_subtopic="Start next available subtopic",
        overall_progress_percent=round(overall_progress_percent, 2),
    )


@router.get("/{user_id}/{language}", response_model=ProgressResponse)
async def get_progress(user_id: str, language: str):
    """Get a user's progress for a specific language."""
    key = f"{user_id}:{language}"
    if key not in _progress_store:
        # Return empty progress for new users
        next_unit = LEARNING_PATH[0]
        return ProgressResponse(
            user_id=user_id,
            language=language,
            completed_units=[],
            completed_subtopics=[],
            current_unit=next_unit,
            current_subtopic="Start first subtopic",
            current_level="beginner",
            total_score=0,
            next_recommended_unit=next_unit,
            next_recommended_subtopic="Start first subtopic",
            overall_progress_percent=0.0,
        )

    record = _progress_store[key]
    next_unit = next(
        (u for u in LEARNING_PATH if u not in record["completed_units"]),
        LEARNING_PATH[-1],
    )

    completed_subtopics = [
        SubtopicProgress(**item) for item in record["completed_subtopics"].values()
    ]

    current_unit = (
        record["completed_units"][-1] if record["completed_units"] else LEARNING_PATH[0]
    )
    current_subtopic = (
        completed_subtopics[-1].subtopic_name if completed_subtopics else "Start first subtopic"
    )
    overall_progress_percent = (len(record["completed_units"]) / len(LEARNING_PATH)) * 100

    return ProgressResponse(
        user_id=user_id,
        language=language,
        completed_units=record["completed_units"],
        completed_subtopics=completed_subtopics,
        current_unit=current_unit,
        current_subtopic=current_subtopic,
        current_level=record["current_level"],
        total_score=record["total_score"],
        next_recommended_unit=next_unit,
        next_recommended_subtopic="Start next available subtopic",
        overall_progress_percent=round(overall_progress_percent, 2),
    )