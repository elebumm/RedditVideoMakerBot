import json

from pathlib import Path
from typing import Dict
from utils import settings
from playwright.async_api import async_playwright, ViewportSize  # pylint: disable=unused-import

from rich.progress import track
import translators as ts

from utils.console import print_step, print_substep

storymode = False


async def download_screenshots_of_reddit_posts(reddit_object: dict, voiced_idx: list):
    """Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        voiced_idx (int): Indexes of voiced comments
    """
    print_step("Downloading screenshots of reddit posts...")

    # ! Make sure the reddit screenshots folder exists
    Path("assets/temp/png").mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        print_substep("Launching Headless Browser...")

        browser = await p.chromium.launch()
        context = await browser.new_context()

        if settings.config["settings"]["theme"] == "dark":
            cookie_file = open("./video_creation/data/cookie-dark-mode.json", encoding="utf-8")
        else:
            cookie_file = open("./video_creation/data/cookie-light-mode.json", encoding="utf-8")
        cookies = json.load(cookie_file)
        await context.add_cookies(cookies)  # load preference cookies
        # Get the thread screenshot
        page = await context.new_page()
        await page.goto(reddit_object["thread_url"], timeout=0)
        await page.set_viewport_size(ViewportSize(width=1920, height=1080))
        if page.locator('[data-testid="content-gate"]').is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            print_substep("Post is NSFW. You are spicy...")
            await page.locator('[data-testid="content-gate"] button').click()
            await page.locator(
                '[data-click-id="text"] button'
            ).click()  # Remove "Click to see nsfw" Button in Screenshot

        # translate code

        if settings.config["reddit"]["thread"]["post_lang"]:
            print_substep("Translating post...")
            texts_in_tl = ts.google(
                reddit_object["thread_title"],
                to_language=settings.config["reddit"]["thread"]["post_lang"],
            )

            await page.evaluate(
                "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > div').textContent = tl_content",
                texts_in_tl,
            )
        else:
            print_substep("Skipping translation...")

        await page.locator('[data-test-id="post-content"]').screenshot(path="assets/temp/png/title.png")

        if storymode:
            await page.locator('[data-click-id="text"]').screenshot(
                path="assets/temp/png/story_content.png"
            )
        else:
            for idx in track(
                    screenshot_num,
                    "Downloading screenshots..."
            ):
                comment = reddit_object["comments"][idx]

                if await page.locator('[data-testid="content-gate"]').is_visible():
                    await page.locator('[data-testid="content-gate"] button').click()

                await page.goto(f'https://reddit.com{comment["comment_url"]}', timeout=0)

                # translate code

                if settings.config["reddit"]["thread"]["post_lang"]:
                    comment_tl = ts.google(
                        comment["comment_body"],
                        to_language=settings.config["reddit"]["thread"]["post_lang"],
                    )
                    await page.evaluate(
                        '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > div[data-testid="comment"] > div`).textContent = tl_content',
                        [comment_tl, comment["comment_id"]],
                    )

                await page.locator(f"#t1_{comment['comment_id']}").screenshot(
                    path=f"assets/temp/png/comment_{idx}.png"
                )

        print_substep("Screenshots downloaded Successfully.", style="bold green")
