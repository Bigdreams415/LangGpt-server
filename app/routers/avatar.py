from fastapi import APIRouter, HTTPException

from app.schemas.avatar_schemas import (
    AvatarGenerateRequest,
    AvatarGenerateResponse,
    AvatarStatusResponse,
)
from app.services import avatar_service

router = APIRouter()


@router.post("/generate", response_model=AvatarGenerateResponse)
async def generate_avatar(request: AvatarGenerateRequest):
    """
    Generate a talking avatar video for the given language.

    The client must provide either:
    - audio_base64: a base64-encoded MP3 or WAV of the lesson audio
    - text: (future) plain text — the backend will generate TTS

    Returns a video_url the Flutter client can play directly.
    """
    if not request.audio_base64:
        raise HTTPException(
            status_code=400,
            detail="audio_base64 is required. Text-to-speech is not yet supported server-side.",
        )

    try:
        result = await avatar_service.generate_avatar_video(
            language=request.language.value,
            audio_base64=request.audio_base64,
            audio_format=request.audio_format or "mp3",
        )
        return AvatarGenerateResponse(**result)

    except FileNotFoundError as e:
        # Avatar image is missing — dev/config issue, not user error
        raise HTTPException(status_code=503, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except RuntimeError as e:
        # SadTalker subprocess failed
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/status", response_model=AvatarStatusResponse)
def avatar_status():
    """
    Health check for the avatar service.
    Confirms SadTalker is installed, the Python env exists,
    and all three avatar images are in place.
    """
    status = avatar_service.check_status()
    return AvatarStatusResponse(
        ready=status["ready"],
        sadtalker_path_exists=status["sadtalker_path_exists"],
        avatars_found=status["avatars_found"],
        message=(
            "Avatar service is ready."
            if status["ready"]
            else "Avatar service is NOT ready. Check /api/v1/avatar/status for details."
        ),
    )