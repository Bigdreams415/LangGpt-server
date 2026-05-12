from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.database import get_db
from app.core.database.redis import get_redis

from app.models.schemas import (
    LessonUnit,
    ProgressResponse,
    ProgressUpdateRequest,
    SubtopicProgress,
)
from app.models.user_model import User, UserProgress
from app.services.lessons_service import TOPICS_METADATA
from password.common.dependencies import get_current_user

router = APIRouter()

# Unit order defines the learning path (beginner to advanced)
LEARNING_PATH = [unit.value for unit in LessonUnit]
TOTAL_SUBTOPICS = sum(len(meta["subtopics"]) for meta in TOPICS_METADATA.values())


def _parse_topic_key(topic_key: str) -> tuple[str, int | None]:
    """Parse stored topic key format: '<unit>:<subtopic_index>' or legacy '<unit>'."""
    if ":" not in topic_key:
        return topic_key, None

    unit, index_text = topic_key.split(":", 1)
    try:
        return unit, int(index_text)
    except ValueError:
        return unit, None


def _build_next_recommendation(
    completed_pairs: set[tuple[str, int]],
) -> tuple[str, str]:
    """Return next (unit, subtopic_name) based on first incomplete subtopic."""
    for unit in LEARNING_PATH:
        unit_meta = TOPICS_METADATA.get(unit)
        if not unit_meta:
            continue

        for idx, subtopic in enumerate(unit_meta["subtopics"]):
            if (unit, idx) not in completed_pairs:
                return unit, subtopic["name"]

    last_unit = LEARNING_PATH[-1]
    last_subtopic = TOPICS_METADATA[last_unit]["subtopics"][-1]["name"]
    return last_unit, last_subtopic


@router.post("/update", response_model=ProgressResponse)
async def update_progress(
    request: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a completed lesson/quiz score for a user. Updates streak and XP."""
    user_uuid = current_user.id
    unit_val = request.unit.value

    existing = await db.scalar(
        select(UserProgress).where(
            and_(
                UserProgress.user_id == user_uuid,
                UserProgress.language == request.language.value,
                UserProgress.topic == unit_val,
                UserProgress.subtopic_index == request.subtopic_index,
            )
        )
    )

    unit_progress = await db.scalar(
        select(UserProgress).where(
            and_(
                UserProgress.user_id == user_uuid,
                UserProgress.language == request.language.value,
                UserProgress.topic == unit_val,
                UserProgress.subtopic_index.is_(None),
            )
        )
    )

    now = datetime.now(timezone.utc)
    if existing:
        existing.score = request.score
        existing.level = request.level.value
        existing.completed = True
        existing.completed_at = now
        existing.attempts = (existing.attempts or 0) + 1
    else:
        db.add(
            UserProgress(
                user_id=user_uuid,
                language=request.language.value,
                topic=unit_val,
                subtopic_index=request.subtopic_index,
                subtopic_name=request.subtopic_name,
                level=request.level.value,
                score=request.score,
                completed=True,
                attempts=1,
                completed_at=now,
            )
        )

    if unit_progress:
        unit_progress.level = request.level.value
        unit_progress.completed = True
        unit_progress.completed_at = now
        unit_progress.attempts = (unit_progress.attempts or 0) + 1
        if unit_progress.score < request.score:
            unit_progress.score = request.score
    else:
        db.add(
            UserProgress(
                user_id=user_uuid,
                language=request.language.value,
                topic=unit_val,
                level=request.level.value,
                score=request.score,
                completed=True,
                attempts=1,
                completed_at=now,
            )
        )

    if existing:
        existing.subtopic_name = request.subtopic_name

    await db.flush()

    rows = (
        await db.scalars(
            select(UserProgress)
            .where(
                and_(
                    UserProgress.user_id == user_uuid,
                    UserProgress.language == request.language.value,
                )
            )
            .order_by(UserProgress.updated_at.asc())
        )
    ).all()

    completed_subtopics: list[SubtopicProgress] = []
    completed_units_set: set[str] = set()
    completed_pairs: set[tuple[str, int]] = set()
    total_score = 0

    for row in rows:
        unit = row.topic
        parsed_index = row.subtopic_index
        if parsed_index is None:
            unit, parsed_index = _parse_topic_key(row.topic)
        if parsed_index is None:
            continue

        subtopics = TOPICS_METADATA.get(unit, {}).get("subtopics", [])
        if not subtopics or parsed_index < 0 or parsed_index >= len(subtopics):
            continue

        completed_units_set.add(unit)
        completed_pairs.add((unit, parsed_index))
        total_score += row.score

        completed_subtopics.append(
            SubtopicProgress(
                unit=unit,
                subtopic_name=row.subtopic_name or subtopics[parsed_index]["name"],
                subtopic_index=parsed_index,
                score=row.score,
                completed=row.completed,
            )
        )

    completed_units = [unit for unit in LEARNING_PATH if unit in completed_units_set]
    next_unit, next_subtopic = _build_next_recommendation(completed_pairs)
    overall_progress_percent = (
        (len(completed_pairs) / TOTAL_SUBTOPICS) * 100 if TOTAL_SUBTOPICS else 0.0
    )

    # Update streak and XP on the user record
    today = datetime.now(timezone.utc).date()
    if current_user.last_activity_date:
        delta = (today - current_user.last_activity_date.date()).days
        if delta == 1:
            current_user.streak_count = (current_user.streak_count or 0) + 1
        elif delta > 1:
            current_user.streak_count = 1
        # delta == 0: same day, no streak change
    else:
        current_user.streak_count = 1

    current_user.last_activity_date = datetime.now(timezone.utc)
    current_user.total_xp = (current_user.total_xp or 0) + 10

    await db.commit()

    return ProgressResponse(
        user_id=str(current_user.id),
        language=request.language.value,
        completed_units=completed_units,
        completed_subtopics=completed_subtopics,
        current_unit=unit_val,
        current_subtopic=request.subtopic_name,
        current_level=request.level.value,
        total_score=total_score,
        next_recommended_unit=next_unit,
        next_recommended_subtopic=next_subtopic,
        overall_progress_percent=round(overall_progress_percent, 2),
        streak_count=current_user.streak_count,
        total_xp=current_user.total_xp,
    )


@router.get("/{user_id}/{language}", response_model=ProgressResponse)
async def get_progress(
    user_id: str,
    language: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a user's progress for a specific language."""
    try:
        user_uuid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid user_id format") from exc

    normalized_language = language.strip().lower()
    language_map = {
        "igbo": "Igbo",
        "yoruba": "Yoruba",
        "hausa": "Hausa",
    }
    if normalized_language not in language_map:
        raise HTTPException(status_code=400, detail="Invalid language")

    language_value = language_map[normalized_language]

    rows = (
        await db.scalars(
            select(UserProgress)
            .where(
                and_(
                    UserProgress.user_id == user_uuid,
                    UserProgress.language == language_value,
                )
            )
            .order_by(UserProgress.updated_at.asc())
        )
    ).all()

    if not rows:
        next_unit, next_subtopic = _build_next_recommendation(set())
        return ProgressResponse(
            user_id=user_id,
            language=language_value,
            completed_units=[],
            completed_subtopics=[],
            current_unit=next_unit,
            current_subtopic=next_subtopic,
            current_level="beginner",
            total_score=0,
            next_recommended_unit=next_unit,
            next_recommended_subtopic=next_subtopic,
            overall_progress_percent=0.0,
        )

    completed_subtopics: list[SubtopicProgress] = []
    completed_units_set: set[str] = set()
    completed_pairs: set[tuple[str, int]] = set()
    total_score = 0

    for row in rows:
        unit = row.topic
        parsed_index = row.subtopic_index
        if parsed_index is None:
            unit, parsed_index = _parse_topic_key(row.topic)
        if parsed_index is None:
            continue

        subtopics = TOPICS_METADATA.get(unit, {}).get("subtopics", [])
        if not subtopics or parsed_index < 0 or parsed_index >= len(subtopics):
            continue

        completed_units_set.add(unit)
        completed_pairs.add((unit, parsed_index))
        total_score += row.score

        completed_subtopics.append(
            SubtopicProgress(
                unit=unit,
                subtopic_name=row.subtopic_name or subtopics[parsed_index]["name"],
                subtopic_index=parsed_index,
                score=row.score,
                completed=row.completed,
            )
        )

    completed_units = [unit for unit in LEARNING_PATH if unit in completed_units_set]
    current_subtopic = completed_subtopics[-1] if completed_subtopics else None
    current_level = rows[-1].level.value if hasattr(rows[-1].level, "value") else str(rows[-1].level)
    next_unit, next_subtopic = _build_next_recommendation(completed_pairs)
    overall_progress_percent = (
        (len(completed_pairs) / TOTAL_SUBTOPICS) * 100 if TOTAL_SUBTOPICS else 0.0
    )

    return ProgressResponse(
        user_id=user_id,
        language=language_value,
        completed_units=completed_units,
        completed_subtopics=completed_subtopics,
        current_unit=current_subtopic.unit if current_subtopic else next_unit,
        current_subtopic=current_subtopic.subtopic_name if current_subtopic else next_subtopic,
        current_level=current_level,
        total_score=total_score,
        next_recommended_unit=next_unit,
        next_recommended_subtopic=next_subtopic,
        overall_progress_percent=round(overall_progress_percent, 2),
    )