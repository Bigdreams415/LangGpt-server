import os
import uuid
import base64
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

from app.core.config.settings import settings


# Path constants — override via .env if needed
# Root of the SadTalker installation (sibling of the backend/ folder)
SADTALKER_ROOT = Path(
    os.getenv("SADTALKER_ROOT", str(Path(__file__).resolve().parents[2] / "sadtalker"))
)

# The actual SadTalker repo (contains inference.py)
SADTALKER_REPO = SADTALKER_ROOT / "SadTalker"

# Folder that holds the three avatar images
AVATARS_DIR = SADTALKER_ROOT / "avatars"

# Python interpreter inside the dedicated sadtalker conda env
SADTALKER_PYTHON = Path(
    os.getenv(
        "SADTALKER_PYTHON",
        str(Path.home() / "miniforge3/envs/sadtalker/bin/python"),
    )
)

# Where generated videos are written and served from
VIDEOS_DIR = Path(__file__).resolve().parents[2] / "static" / "videos"

# Base URL prefix used to build the public video URL
# e.g. "http://localhost:8000/static/videos"
STATIC_BASE_URL = os.getenv("STATIC_BASE_URL", "http://localhost:8000/static/videos")

# Temporary audio uploads
TEMP_AUDIO_DIR = Path(__file__).resolve().parents[2] / "static" / "temp_audio"

# Map language name → avatar image filename
AVATAR_MAP: dict[str, str] = {
    "Igbo": "igbo.png",
    "Yoruba": "yoruba.png",
    "Hausa": "hausa.png",
}


def _ensure_dirs() -> None:
    """Create output directories if they don't exist yet."""
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def _avatar_path(language: str) -> Path:
    """Return the absolute path to the avatar image for a given language."""
    filename = AVATAR_MAP.get(language)
    if not filename:
        raise ValueError(f"No avatar configured for language: {language}")
    path = AVATARS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Avatar image not found at {path}. "
            f"Please place {filename} in {AVATARS_DIR}."
        )
    return path


def _decode_audio(audio_base64: str, audio_format: str, job_id: str) -> Path:
    """
    Decode a base64 audio string and write it to a temp file.
    Returns the path to the written file.
    """
    audio_bytes = base64.b64decode(audio_base64)
    audio_path = TEMP_AUDIO_DIR / f"{job_id}.{audio_format}"
    audio_path.write_bytes(audio_bytes)
    return audio_path


def _build_sadtalker_command(
    audio_path: Path,
    image_path: Path,
    output_dir: Path,
) -> list[str]:
    """
    Build the SadTalker subprocess command.
    Uses the dedicated Python interpreter in the sadtalker conda env.
    """
    return [
        str(SADTALKER_PYTHON),
        str(SADTALKER_REPO / "inference.py"),
        "--driven_audio", str(audio_path),
        "--source_image", str(image_path),
        "--result_dir", str(output_dir),
        "--enhancer", "gfpgan",
        "--preprocess", "crop",
        "--still",                      # keeps head natural for teacher look
        "--size", "256",                # faster; use 512 for higher quality
    ]


def _find_generated_video(output_dir: Path) -> Path | None:
    """
    SadTalker writes the enhanced video with a timestamped subfolder.
    Walk the output_dir and return the *_enhanced.mp4 if it exists,
    otherwise the plain .mp4.
    """
    enhanced = list(output_dir.rglob("*_enhanced.mp4"))
    if enhanced:
        return enhanced[0]
    plain = list(output_dir.rglob("*.mp4"))
    return plain[0] if plain else None


def _move_to_videos(src: Path, job_id: str) -> Path:
    """Move the generated video to the public static/videos folder."""
    dest = VIDEOS_DIR / f"{job_id}.mp4"
    src.rename(dest)
    return dest


def check_status() -> dict:
    """
    Return a readiness dict — used by the health endpoint so the team
    can quickly spot missing files or misconfigured paths.
    """
    avatars_found = {}
    for lang, filename in AVATAR_MAP.items():
        avatars_found[lang] = (AVATARS_DIR / filename).exists()

    return {
        "ready": SADTALKER_REPO.exists() and SADTALKER_PYTHON.exists(),
        "sadtalker_path_exists": SADTALKER_REPO.exists(),
        "sadtalker_python_exists": SADTALKER_PYTHON.exists(),
        "avatars_found": avatars_found,
        "paths": {
            "sadtalker_repo": str(SADTALKER_REPO),
            "sadtalker_python": str(SADTALKER_PYTHON),
            "avatars_dir": str(AVATARS_DIR),
            "videos_dir": str(VIDEOS_DIR),
        },
    }


async def generate_avatar_video(
    language: str,
    audio_base64: str,
    audio_format: str = "mp3",
) -> dict:
    """
    Main entry point called by the router.

    Steps:
      1. Decode & save the incoming audio
      2. Resolve the correct avatar image
      3. Run SadTalker in a subprocess (non-blocking via asyncio)
      4. Move the output video to static/videos/
      5. Clean up temp audio
      6. Return a dict matching AvatarGenerateResponse

    Raises:
      ValueError  – bad language or missing avatar
      RuntimeError – SadTalker process failed
    """
    _ensure_dirs()

    job_id = f"{language.lower()}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    output_dir = VIDEOS_DIR / f"tmp_{job_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    audio_path: Path | None = None

    try:
        # 1. Save audio
        audio_path = _decode_audio(audio_base64, audio_format, job_id)

        # 2. Resolve avatar image
        image_path = _avatar_path(language)

        # 3. Build + run SadTalker subprocess
        cmd = _build_sadtalker_command(audio_path, image_path, output_dir)

        loop = asyncio.get_event_loop()
        process_result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(SADTALKER_REPO),
                timeout=300,    # 5-minute hard limit per video
            ),
        )

        if process_result.returncode != 0:
            raise RuntimeError(
                f"SadTalker failed (exit {process_result.returncode}):\n"
                f"{process_result.stderr[-2000:]}"   # last 2k chars of stderr
            )

        # 4. Find & move the output video
        generated = _find_generated_video(output_dir)
        if not generated:
            raise RuntimeError("SadTalker finished but no output video was found.")

        final_path = _move_to_videos(generated, job_id)
        video_url = f"{STATIC_BASE_URL}/{job_id}.mp4"

        return {
            "language": language,
            "video_url": video_url,
            "video_filename": f"{job_id}.mp4",
            "message": "Avatar video generated successfully",
        }

    finally:
        # Always clean up temp audio and tmp output dir
        if audio_path and audio_path.exists():
            audio_path.unlink(missing_ok=True)
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)