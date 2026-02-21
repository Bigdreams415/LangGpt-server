from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    QuizRequest, QuizResponse,
    CheckAnswerRequest, CheckAnswerResponse
)
from app.services.gemini import generate
from app.prompts.templates import quiz_prompt, check_answer_prompt

router = APIRouter()


@router.post("/", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate a multiple-choice quiz for a given language, topic, and level."""
    try:
        prompt = quiz_prompt(
            request.language,
            request.level,
            request.topic,
            request.num_questions,
        )
        data = await generate(prompt, expect_json=True)
        return QuizResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.post("/check", response_model=CheckAnswerResponse)
async def check_answer(request: CheckAnswerRequest):
    """Check a user's answer and provide feedback."""
    try:
        prompt = check_answer_prompt(
            request.language,
            request.question,
            request.user_answer,
            request.correct_answer,
        )
        data = await generate(prompt, expect_json=True)
        return CheckAnswerResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer checking failed: {str(e)}")