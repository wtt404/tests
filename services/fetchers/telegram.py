import re
import html
import aiohttp

from models.post import Post, Media
from services.fetchers.base import Fetcher

URL_PATTERN = re.compile(r"t\.me/(?:s/)?([A-Za-z0-9_]+)/(\d+)")

TEXT_PATTERN = re.compile(
    r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
    re.DOTALL
)
PHOTO_PATTERN = re.compile(
    r'tgme_widget_message_photo_wrap"[^>]*style="[^"]*background-image:url\(\'([^\']+)\'\)'
)
VIDEO_PATTERN = re.compile(r'<video[^>]+src="([^"]+)"')


def _clean_text(raw: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", raw)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


class TelegramFetcher(Fetcher):
    async def fetch(self, url: str) -> Post:
        match = URL_PATTERN.search(url)

        if not match:
            raise RuntimeError(
                "Unsupported Telegram URL (private/invite-only channels aren't supported)"
            )

        channel, msg_id = match.groups()
        embed_url = f"https://t.me/{channel}/{msg_id}?embed=1&mode=tme"

        async with aiohttp.ClientSession() as session:
            async with session.get(embed_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Telegram returned status {resp.status}")

                body = await resp.text()

        if "tgme_widget_message" not in body:
            raise RuntimeError("Telegram post not found or channel is private")

        text_match = TEXT_PATTERN.search(body)
        text = _clean_text(text_match.group(1)) if text_match else ""

        seen = set()
        media = []

        for photo_url in PHOTO_PATTERN.findall(body):
            photo_url = photo_url.replace("&amp;", "&")

            if photo_url in seen:
                continue

            seen.add(photo_url)
            media.append(Media(url=photo_url, type="image"))

        for video_url in VIDEO_PATTERN.findall(body):
            video_url = video_url.replace("&amp;", "&")

            if video_url in seen:
                continue

            seen.add(video_url)
            media.append(Media(url=video_url, type="video"))

        return Post(platform="telegram", text=text, media=media)
