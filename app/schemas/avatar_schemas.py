from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum


class AvatarLanguage(str, Enum):
    igbo = "Igbo"
    yoruba = "Yoruba"
    hausa = "Hausa"


class AvatarGenerateRequest(BaseModel):
    """
    Request to generate a talking avatar video.

    The client sends either:
      - audio_base64: a base64-encoded audio file (mp3 or wav)
      - text: plain text the avatar should speak (backend generates TTS)

    Exactly one of the two must be provided.
    """
    language: AvatarLanguage
    audio_base64: Optional[str] = None     # base64-encoded mp3/wav
    audio_format: Optional[str] = "mp3"   # "mp3" | "wav"
    text: Optional[str] = None             # future: server-side TTS

    @field_validator("audio_base64", "text", mode="before")
    @classmethod
    def at_least_one_input(cls, v, info):
        return v

    def model_post_init(self, __context):
        if not self.audio_base64 and not self.text:
            raise ValueError("Provide either audio_base64 or text.")


class AvatarGenerateResponse(BaseModel):
    """Successful avatar generation response."""
    language: str
    video_url: str          # relative URL served by FastAPI static files
    video_filename: str     # just the filename, useful for caching on client
    duration_seconds: Optional[float] = None
    message: str = "Avatar video generated successfully"


class AvatarStatusResponse(BaseModel):
    """Health/readiness check for the avatar service."""
    ready: bool
    sadtalker_path_exists: bool
    avatars_found: dict      # {"Igbo": True, "Yoruba": False, "Hausa": True}
    message: str