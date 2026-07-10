from models.post import Post, Media
from services.browser import new_page
from services.fetchers.base import Fetcher
import json
import re


class XFetcher(Fetcher):
    async def fetch(self, url: str) -> Post:

        page = await new_page()
        captured_video_urls = set()

        def _capture_video(response):
            resp_url = response.url
            if "video.twimg.com" in resp_url and (".m3u8" in resp_url or ".mp4" in resp_url):
                captured_video_urls.add(resp_url)

        page.on("response", _capture_video)

        try:
            print("FETCH START", flush=True)

            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )
            print("Navigation finished", flush=True)

            print(f"Status: {response.status if response else 'None'}", flush=True)

            print("Current URL:", page.url, flush=True)

            print("Title:", await page.title(), flush=True)

            # Multi-photo galleries render a beat after domcontentloaded fires;
            # wait for at least one media element, then give the rest of the
            # gallery a moment to finish attaching before we scrape the HTML.
            try:
                await page.wait_for_selector(
                    '[data-testid="tweetPhoto"], video',
                    timeout=8000
                )
                await page.wait_for_timeout(750)
            except Exception:
                pass  # text-only tweet, nothing to wait for

            # X frequently doesn't fetch the actual video manifest until
            # playback starts, so it's often just not present in the static
            # HTML at all. Nudge the player and give the network request a
            # moment to fire; we're listening for it via page.on("response").
            try:
                video_el = page.locator("video").first
                if await video_el.count() > 0:
                    await video_el.click(timeout=3000)
                    await page.wait_for_timeout(1500)
            except Exception:
                pass

            scripts = await page.locator('script[type="application/ld+json"]').all_inner_texts()

            data = None

            for script in scripts:
                obj = json.loads(script)
          
                if obj.get("@type") == "SocialMediaPosting":
                    data = obj
                    break

            if data is None:
                raise RuntimeError("SocialMediaPosting not found")

            text = data["articleBody"]
            html = await page.content()
            video_urls = set(re.findall(
                r'https://video\.twimg\.com[^"\']+',
                html
            ))
            video_urls |= captured_video_urls

            print("Video playlists:", video_urls, flush=True)
  
            seen = set()
            media = []

            for media_url in re.findall(r'https://pbs\.twimg\.com/media/[^"\']+', html):
                media_url = media_url.replace("&amp;", "&")

                if "?format=webp" in media_url:
                    continue

                if media_url in seen:
                    continue
       
                seen.add(media_url)

                media.append(
                    Media(
                        url=media_url,
                        type="image"
                    )
                )

            for video_url in video_urls:
                video_url = video_url.replace("&amp;", "&")

                if video_url in seen:
                    continue 

                seen.add(video_url)

                media.append(
                    Media(
                        url=video_url,
                        type="video"
                    )
                )

            return Post(
                platform="x",
                text=text,
                media=media
            )

        finally:
            page.remove_listener("response", _capture_video)
            await page.close()