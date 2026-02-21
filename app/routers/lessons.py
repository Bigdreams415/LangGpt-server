from fastapi import APIRouter, HTTPException
from app.models.schemas import LessonRequest, LessonResponse, TranslationRequest, TranslationResponse
from app.services.gemini import generate
from app.prompts.templates import lesson_prompt, translation_prompt

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