from tools import TOOLS

async def translate(text: str) -> str:
    return await TOOLS["translate"].execute(text)