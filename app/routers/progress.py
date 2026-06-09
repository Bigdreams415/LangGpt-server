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

# A quiz counts as "passed" (and the unit as completed) at this score or above.
# This matches the threshold the Flutter client uses to show the pass dialog.
PASS_THRESHOLD = 80


def _parse_topic_key(topic_key: str) -> tuple[str, int | None]:
    """Parse stored topic key format: '<unit>:<subtopic_index>' or legacy '<unit>'."""
    if ":" not in topic_key:
        return topic_key, None

    unit, index_text = topic_key.split(":", 1)
    try:
        return unit, int(index_text)
    except ValueError:
        return unit, None


def _first_subtopic_name(unit: str) -> str:
    """Name of a unit's first subtopic, or empty string if the unit is unknown."""
    subtopics = TOPICS_METADATA.get(unit, {}).get("subtopics", [])
    return subtopics[0]["name"] if subtopics else ""


def _build_next_unit_recommendation(
    completed_units_set: set[str],
) -> tuple[str, str]:
    """Return the next (unit, first_subtopic_name) the learner should open.

    Progression is unit-by-unit: passing a unit's quiz completes that unit and
    points the learner at the next not-yet-completed unit.
    """
    for unit in LEARNING_PATH:
        if unit not in completed_units_set:
            return unit, _first_subtopic_name(unit)

    last_unit = LEARNING_PATH[-1]
    return last_unit, _first_subtopic_name(last_unit)


def _build_unlocked_units(completed_units_set: set[str]) -> list[str]:
    """Units the learner may open: every completed unit plus the next one.

    Walks the learning path in order and stops right after the first unit that
    is not completed, so units stay locked until the previous one is passed.
    """
    unlocked: list[str] = []
    for unit in LEARNING_PATH:
        unlocked.append(unit)
        if unit not in completed_units_set:
            break
    return unlocked


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
    # Only a passing score completes the lesson. A failed attempt is still
    # recorded (best score kept, attempts incremented) but never unlocks the
    # next unit. Once a unit is completed it stays completed.
    passed = request.score >= PASS_THRESHOLD

    if existing:
        existing.score = max(existing.score or 0, request.score)
        existing.level = request.level.value
        existing.attempts = (existing.attempts or 0) + 1
        existing.subtopic_name = request.subtopic_name
        if passed:
            existing.completed = True
            existing.completed_at = now
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
                completed=passed,
                attempts=1,
                completed_at=now if passed else None,
            )
        )

    if unit_progress:
        unit_progress.level = request.level.value
        unit_progress.attempts = (unit_progress.attempts or 0) + 1
        if unit_progress.score < request.score:
            unit_progress.score = request.score
        if passed:
            unit_progress.completed = True
            unit_progress.completed_at = now
    else:
        db.add(
            UserProgress(
                user_id=user_uuid,
                language=request.language.value,
                topic=unit_val,
                level=request.level.value,
                score=request.score,
                completed=passed,
                attempts=1,
                completed_at=now if passed else None,
            )
        )

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

        # Only passing rows complete a unit and count toward unlocking.
        if row.completed:
            completed_units_set.add(unit)
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
    unlocked_units = _build_unlocked_units(completed_units_set)
    next_unit, next_subtopic = _build_next_unit_recommendation(completed_units_set)
    overall_progress_percent = (
        (len(completed_units) / len(LEARNING_PATH)) * 100 if LEARNING_PATH else 0.0
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
        unlocked_units=unlocked_units,
        completed_subtopics=completed_subtopics,
        current_unit=next_unit,
        current_subtopic=next_subtopic,
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a user's progress for a specific language."""
    try:
        user_uuid = UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid user_id format") from exc

    if str(current_user.id) != str(user_uuid):
        raise HTTPException(status_code=403, detail="Access denied")

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
        next_unit, next_subtopic = _build_next_unit_recommendation(set())
        return ProgressResponse(
            user_id=user_id,
            language=language_value,
            completed_units=[],
            unlocked_units=_build_unlocked_units(set()),
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

        # Only passing rows complete a unit and count toward unlocking.
        if row.completed:
            completed_units_set.add(unit)
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
    unlocked_units = _build_unlocked_units(completed_units_set)
    current_level = rows[-1].level.value if hasattr(rows[-1].level, "value") else str(rows[-1].level)
    next_unit, next_subtopic = _build_next_unit_recommendation(completed_units_set)
    overall_progress_percent = (
        (len(completed_units) / len(LEARNING_PATH)) * 100 if LEARNING_PATH else 0.0
    )

    return ProgressResponse(
        user_id=user_id,
        language=language_value,
        completed_units=completed_units,
        unlocked_units=unlocked_units,
        completed_subtopics=completed_subtopics,
        current_unit=next_unit,
        current_subtopic=next_subtopic,
        current_level=current_level,
        total_score=total_score,
        next_recommended_unit=next_unit,
        next_recommended_subtopic=next_subtopic,
        overall_progress_percent=round(overall_progress_percent, 2),
    )