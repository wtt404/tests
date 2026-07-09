from services.fetchers import FETCHERS
from services.pipeline import translate_post

async def dispatch(message, result):
    fetcher = FETCHERS.get(result.type)

    if fetcher is None:
        return

    post = await fetcher.fetch(result.url)

    await translate_post(message, post)