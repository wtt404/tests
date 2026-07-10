from models.post import Post, Media
from services.browser import new_page
from services.fetchers.base import Fetcher
import json
import re


class XFetcher(Fetcher):
    async def fetch(self, url: str) -> Post:

        page = await new_page()

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
            video_urls = re.findall(
                r'https://video\.twimg\.com[^"\']+',
                html
            )

            print(video_urls, flush=True) 
            print("Video playlists:", video_urls, flush=True)
  
            seen = set()
            media = []

            for url in re.findall(r'https://pbs\.twimg\.com/media/[^"\']+', html):
                url = url.replace("&amp;", "&")

                if "?format=webp" in url:
                    continue

                if url in seen:
                    continue
       
                seen.add(url)

                media.append(
                    Media(
                        url=url,
                        type="image"
                    )
                )

            for url in video_urls:
                url=url.replace("&amp;", "&") 

                if url in seen:
                    continue 

                seen.add(url)

                media.append(
                    Media(
                        url=url,
                        type="video"
                    )
                )

            return Post(
                platform="x",
                text=text,
                media=media
            )

        finally:
            await page.close()