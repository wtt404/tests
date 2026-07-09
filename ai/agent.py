from google.genai import types

from ai.client import client
from ai.prompts import SYSTEM_PROMPT


MODEL = "gemini-2.5-flash"


async def ai(message: str):
    response = client.models.generate_content(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
        contents=message,
    )

    return response.text