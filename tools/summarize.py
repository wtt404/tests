from google.genai import types
from ai.client import client
from tools.base import Tool

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You summarize text clearly and concisely.

Rules:
- Keep it short - a few sentences, unless the user explicitly asks for more detail.
- Preserve the key facts, names, numbers, and claims. Do not lose specifics.
- Do not add opinions or information not present in the original text.
- Do not pad with filler phrases like "This text discusses..." - get straight to the content.
"""

class SummarizeTool(Tool):
    name = "summarize"
    description = "Summarize a piece of text concisely, preserving key facts."
    parameters_json_schema = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to summarize.",
            },
        },
        "required": ["text"],
    }

    async def execute(self, text: str):
        try:
            response = client.models.generate_content(
                model=MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
                contents=text,
            )
            return response.text
        except Exception as e:
            print("Summarize failed:", e, flush=True)
            return None
