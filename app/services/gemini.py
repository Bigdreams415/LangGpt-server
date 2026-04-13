import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
import asyncio

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


def _clean_json(text: str) -> str:
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())
    return text.strip()


async def generate(prompt: str, expect_json: bool = True) -> str | dict:
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=8192,  
    )

    # genai client is sync — run in thread to avoid blocking event loop
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config,
        )
    )

    text = response.text.strip()

    if expect_json:
        text = _clean_json(text)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Log what Gemini actually returned to help debug
            print(f"[Gemini] JSON parse failed: {e}")
            print(f"[Gemini] Raw response (first 500 chars): {text[:500]}")
            raise ValueError(f"Gemini returned invalid JSON: {e}")

    return text