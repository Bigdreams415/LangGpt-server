from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.schemas import LessonRequest, LessonResponse, TranslationRequest, TranslationResponse
from app.services.gemini import generate
from app.prompts.templates import lesson_prompt, translation_prompt
from app.schemas.lessons_schemas import LessonsListResponse, LessonDetailResponse
from app.services.lessons_service import lessons_service

router = APIRouter()


@router.post("/", response_model=LessonResponse)
async def get_lesson(request: LessonRequest):
    """Generate a vocabulary and culture lesson for a given topic and level."""
    try:
        prompt = lesson_prompt(request.language, request.level, request.topic)
        data = await generate(prompt, expect_json=True)
        return LessonResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson generation failed: {str(e)}")


@router.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """Translate text to or from any of the supported languages."""
    try:
        prompt = translation_prompt(request.text, request.from_language, request.to_language)
        data = await generate(prompt, expect_json=True)
        return TranslationResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.get("/topics")
def get_topics():
    """Return all available lesson topics."""
    from app.models.schemas import LessonTopic
    return {"topics": [t.value for t in LessonTopic]}


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
    limit: int = Query(20, ge=1, le=100, description="Number of topics to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """Get a paginated list of all available lessons for a language."""
    return lessons_service.get_lessons_list(
        language=language,
        level=level,
        limit=limit,
        offset=offset,
    )


@router.get("/topic/{language}/{topic_id}", response_model=LessonDetailResponse)
async def get_lesson_by_id(language: str, topic_id: str):
    """Get detailed lesson content for a specific topic."""
    return lessons_service.get_lesson_detail(language, topic_id)