from fastapi import APIRouter, HTTPException
from app.models.schemas import ConversationRequest, ConversationResponse
from app.services.gemini import generate
from app.prompts.templates import conversation_prompt

router = APIRouter()


@router.post("/", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    """
    Have a conversation with the AI tutor in the target language.
    Pass conversation_history as a list of {role, content} dicts to maintain context.
    """
    try:
        prompt = conversation_prompt(
            request.language,
            request.level,
            request.topic,
            request.conversation_history or [],
            request.user_message,
        )
        data = await generate(prompt, expect_json=True)
        return ConversationResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation failed: {str(e)}")