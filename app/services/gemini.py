import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash-lite"  # Use the latest Gemini model available

async def generate(prompt: str, expect_json: bool = True) -> str | dict:
    """
    Core function to call Gemini. Returns parsed dict if expect_json=True,
    otherwise returns raw string.
    """
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=config,
    )

    text = response.text.strip()

    if expect_json:
        # Strip markdown code fences if Gemini wraps output in ```json
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    return text