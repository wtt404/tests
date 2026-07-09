from google.genai import types
from deep_translator import DeeplTranslator
from ai.client import client
from config import settings

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = f"""
You are a professional translator.

Translate the user's text into {settings.TARGET_LANGUAGE}.

Rules:
- Preserve the original meaning.
- Preserve formatting.
- Do not add explanations.
- Do not summarize.
- Output only the translation.
"""

class TranslateTool:
    name = "translate"
    description = "Translate text."

    async def execute(self, text: str):
        try:
            response = client.models.generate_content(
                model=MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
                contents=text,
            )

            print(response, flush=True)

            return response.text.strip()

        except Exception as e:
            print("Gemini failed:", e, flush=True)

        try:
            translated = DeeplTranslator(
                source="auto",
                target="en"
            ).translate(text)

            return translated

        except Exception as e:
            print("DeepL failed:", e, flush=True)
            return None