from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.models.schemas import LessonRequest, LessonResponse, TranslationRequest, TranslationResponse, LessonUnit
from app.models.user_model import User
from app.services.gemini import generate, GeminiUnavailableError
from app.prompts.templates import lesson_prompt, translation_prompt
from app.schemas.lessons_schemas import LessonsListResponse, LessonDetailResponse
from app.services.lessons_service import lessons_service
from password.common.dependencies import get_current_user

router = APIRouter()


def _resolve_subtopic_name(
    requested_subtopic: str | None,
    indexed_subtopic: str,
) -> str:
    """Ensure optional subtopic override matches the indexed subtopic."""
    if not requested_subtopic:
        return indexed_subtopic

    normalized_requested = " ".join(requested_subtopic.strip().lower().split())
    normalized_indexed = " ".join(indexed_subtopic.strip().lower().split())

    if normalized_requested != normalized_indexed:
        raise HTTPException(
            status_code=400,
            detail=(
                "subtopic_name does not match subtopic_index for this unit. "
                f"Expected subtopic '{indexed_subtopic}' for the provided index."
            ),
        )

    return indexed_subtopic


@router.post("/", response_model=LessonResponse)
async def get_lesson(
    request: LessonRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate a vocabulary and culture lesson for a given unit and subtopic."""
    try:
        language = request.language.value
        level = request.level.value
        unit = request.unit.value

        subtopic_meta = lessons_service.get_subtopic_detail(
            language=language,
            unit_id=unit,
            subtopic_index=request.subtopic_index,
        )

        chosen_subtopic = _resolve_subtopic_name(
            requested_subtopic=request.subtopic_name,
            indexed_subtopic=subtopic_meta["subtopic_name"],
        )

        unit_detail = lessons_service.get_lesson_detail(language, unit)
        total_subtopics = len(unit_detail.subtopics)

        prompt = lesson_prompt(
            language=language,
            level=level,
            unit=unit,
            subtopic=chosen_subtopic,
            subtopic_index=request.subtopic_index,
            total_subtopics=total_subtopics,
            next_subtopic=subtopic_meta["next_subtopic_name"],
        )
        data = await generate(prompt, expect_json=True)
        return LessonResponse(**data)
    except GeminiUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="The lesson service is busy right now. Please try again in a moment.",
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[lessons] Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong generating your lesson. Please try again.",
        )


@router.post("/translate", response_model=TranslationResponse)
async def translate(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user),
):
    """Translate text to or from any of the supported languages."""
    try:
        prompt = translation_prompt(request.text, request.from_language, request.to_language.value)
        data = await generate(prompt, expect_json=True)
        return TranslationResponse(**data)
    except GeminiUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="The translation service is busy right now. Please try again in a moment.",
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[lessons/translate] Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong with the translation. Please try again.",
        )


@router.get("/units")
def get_units():
    """Return all available lesson units."""
    return {"units": [t.value for t in LessonUnit]}


@router.get("/languages")
def get_languages():
    """Return all supported languages."""
    return {
        "languages": [
            {"code": "igbo", "name": "Igbo", "region": "Southeast Nigeria", "speakers": "~45 million"},
            {"code": "yoruba", "name": "Yoruba", "region": "Southwest Nigeria", "speakers": "~50 million"},
            {"code": "hausa", "name": "Hausa", "region": "North Nigeria", "speakers": "~80 million"},
        ]
    }


@router.get("/list/{language}", response_model=LessonsListResponse)
async def list_lessons(
    language: str,
    level: Optional[str] = Query(None, description="Filter by level: beginner, intermediate, advanced"),
    limit: int = Query(20, ge=1, le=100, description="Number of units to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
):
    """Get a paginated list of all available lessons for a language."""
    return lessons_service.get_lessons_list(
        language=language,
        level=level,
        limit=limit,
        offset=offset,
    )


@router.get("/unit/{language}/{unit_id}", response_model=LessonDetailResponse)
async def get_unit_by_id(
    language: str,
    unit_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed lesson content for a specific unit."""
    return lessons_service.get_lesson_detail(language, unit_id)