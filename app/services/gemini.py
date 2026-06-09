import os
import json
import re
import asyncio
from google import genai
from google.genai import types, errors as genai_errors
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"

# Max attempts before giving up on a transient Gemini error
_MAX_RETRIES = 3
# Backoff delays in seconds between attempts (1s, 2s, 4s)
_BACKOFF = [1, 2, 4]


class GeminiUnavailableError(Exception):
    """Raised when Gemini returns a transient server error on all retry attempts."""


def _clean_json(text: str) -> str:
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())
    return text.strip()


def _is_transient(exc: Exception) -> bool:
    """Return True for Gemini server-side errors that are worth retrying."""
    if isinstance(exc, genai_errors.ServerError):
        return True
    if isinstance(exc, genai_errors.APIError):
        # APIError exposes the HTTP status on .code
        code = getattr(exc, "code", None)
        return code is not None and code >= 500
    return False


async def generate(prompt: str, expect_json: bool = True) -> str | dict:
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=8192,
    )

    last_exc: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        try:
            # genai client is sync — run in thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                    config=config,
                ),
            )

            # Guard against safety blocks / empty completions
            if not response.text:
                raise ValueError("Gemini returned an empty response (possible safety block)")

            text = response.text.strip()

            if expect_json:
                text = _clean_json(text)
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    print(f"[Gemini] JSON parse failed: {e}")
                    print(f"[Gemini] Raw response (first 500 chars): {text[:500]}")
                    raise ValueError(f"Gemini returned invalid JSON: {e}")

            return text

        except Exception as exc:
            if _is_transient(exc):
                last_exc = exc
                wait = _BACKOFF[attempt] if attempt < len(_BACKOFF) else _BACKOFF[-1]
                print(f"[Gemini] Transient error on attempt {attempt + 1}/{_MAX_RETRIES}: {exc}. Retrying in {wait}s...")
                await asyncio.sleep(wait)
                continue
            # Non-transient error — re-raise immediately
            raise

    # All retries exhausted
    print(f"[Gemini] All {_MAX_RETRIES} attempts failed. Last error: {last_exc}")
    raise GeminiUnavailableError("Gemini service is temporarily unavailable") from last_exc