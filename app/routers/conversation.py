from fastapi import APIRouter, HTTPException
from app.models.schemas import ConversationRequest, ConversationResponse
from app.services.gemini import generate
from app.prompts.templates import conversation_prompt
from app.services.lessons_service import lessons_service

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


@router.post("/", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    """
    Have a conversation with the AI tutor in the target language.
    Pass conversation_history as a list of {role, content} dicts to maintain context.
    """
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

        prompt = conversation_prompt(
            language=language,
            level=level,
            unit=unit,
            subtopic=chosen_subtopic,
            history=request.conversation_history or [],
            user_message=request.user_message,
        )
        data = await generate(prompt, expect_json=True)
        return ConversationResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation failed: {str(e)}")