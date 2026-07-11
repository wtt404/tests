from google.genai import types

from ai.client import client
from ai.prompts import SYSTEM_PROMPT
from tools import TOOLS


MODEL = "gemini-2.5-flash"
MAX_TOOL_TURNS = 3


def _build_tools():
    declarations = [
        types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters_json_schema=tool.parameters_json_schema,
        )
        for tool in TOOLS.values()
    ]

    return [types.Tool(function_declarations=declarations)]


async def ai(message: str, images: list = None) -> str:
    tools = _build_tools()

    parts = []

    for image_bytes, mime_type in (images or []):
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

    parts.append(types.Part.from_text(
        text=message or "Read any text in the attached image(s) and translate it."
    ))

    contents = [types.Content(role="user", parts=parts)]

    for _ in range(MAX_TOOL_TURNS):
        response = client.models.generate_content(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=tools,
            ),
            contents=contents,
        )

        print(f"finish_reason: {getattr(response.candidates[0], 'finish_reason', None) if response.candidates else 'no candidates'}", flush=True)

        if not response.candidates:
            feedback = getattr(response, "prompt_feedback", None)
            print(f"No candidates returned. prompt_feedback={feedback}", flush=True)
            return "I couldn't process that — it may have been blocked by a content filter."

        calls = response.function_calls

        if not calls:
            if not response.text:
                return "I couldn't come up with a text response for that."
            return response.text

        # Keep the model's own function-call turn in the conversation history.
        contents.append(response.candidates[0].content)

        function_response_parts = []

        for call in calls:
            print(f"AI TOOL CALL: {call.name} args={call.args}", flush=True)
            tool = TOOLS.get(call.name)

            if tool is None:
                result = {"error": f"Unknown tool: {call.name}"}
            else:
                try:
                    output = await tool.execute(**(call.args or {}))
                    result = {"result": output}
                except Exception as e:
                    print(f"Tool '{call.name}' failed:", e, flush=True)
                    result = {"error": str(e)}

            function_response_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response=result,
                )
            )

        contents.append(types.Content(role="tool", parts=function_response_parts))

    return "I tried using a tool a few times but couldn't finish that one — try rephrasing?"
