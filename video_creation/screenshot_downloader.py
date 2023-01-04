import json
import re
from pathlib import Path
from typing import Dict, Final

import translators as ts
from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright
from rich.progress import track

from utils import settings
from utils.console import print_step, print_substep
from utils.imagenarator import imagemaker


__all__ = ["download_screenshots_of_reddit_posts"]

def get_screenshots_of_reddit_posts(reddit_object: dict, screenshot_num: int):
    """Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """
    # settings values
    W: Final[int] = int(settings.config["settings"]["resolution_w"])
    H: Final[int] = int(settings.config["settings"]["resolution_h"])
    lang: Final[str] = settings.config["reddit"]["thread"]["post_lang"]
    storymode: Final[bool] = settings.config["settings"]["storymode"]

    print_step("Downloading screenshots of reddit posts...")
    reddit_id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
    # ! Make sure the reddit screenshots folder exists
    Path(f"assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

    screenshot_num: int
    with sync_playwright() as p:
        print_substep("Launching Headless Browser...")

        browser = p.chromium.launch()  # headless=False #to check for chrome view
        context = browser.new_context()
        # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
        # When the dsf is 1, the width of the screenshot is 600 pixels
        # so we need a dsf such that the width of the screenshot is greater than the final resolution of the video
        dsf = (W // 600) + 1

        context = browser.new_context(
            locale=lang or "en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=W, height=H),
            device_scale_factor=dsf,
        )
        # set the theme and disable non-essential cookies
        if settings.config["settings"]["theme"] == "dark":
            cookie_file = open(
                "./video_creation/data/cookie-dark-mode.json", encoding="utf-8"
            )
            bgcolor = (33, 33, 36, 255)
            txtcolor = (240, 240, 240)
        else:
            cookie_file = open(
                "./video_creation/data/cookie-light-mode.json", encoding="utf-8"
            )
            bgcolor = (255, 255, 255, 255)
            txtcolor = (0, 0, 0)
        if storymode and settings.config["settings"]["storymodemethod"] == 1:
            # for idx,item in enumerate(reddit_object["thread_post"]):
            return imagemaker(theme=bgcolor, reddit_obj=reddit_object, txtclr=txtcolor)
        cookies = json.load(cookie_file)
        cookie_file.close()

        context.add_cookies(cookies)  # load preference cookies

        # Get the thread screenshot
        page = context.new_page()
        page.goto(reddit_object["thread_url"], timeout=0)
        page.set_viewport_size(ViewportSize(width=W, height=H))

        if page.locator('[data-testid="content-gate"]').is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            print_substep("Post is NSFW. You are spicy...")
            page.locator('[data-testid="content-gate"] button').click()
            page.wait_for_load_state()  # Wait for page to fully load

            if page.locator('[data-click-id="text"] button').is_visible():
                page.locator(
                    '[data-click-id="text"] button'
                ).click()  # Remove "Click to see nsfw" Button in Screenshot

            # translate code

        if lang:
            print_substep("Translating post...")
            texts_in_tl = ts.google(
                reddit_object["thread_title"],
                to_language=lang,
            )

            page.evaluate(
                "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > div').textContent = tl_content",
                texts_in_tl,
            )
        else:
            print_substep("Skipping translation...")

        postcontentpath = f"assets/temp/{reddit_id}/png/title.png"
        page.locator('[data-test-id="post-content"]').screenshot(path=postcontentpath)

        if storymode:
            page.locator('[data-click-id="text"]').first.screenshot(
                path=f"assets/temp/{reddit_id}/png/story_content.png"
            )
        else:
            for idx, comment in enumerate(
                    track(
                        reddit_object["comments"][:screenshot_num],
                        "Downloading screenshots...",
                    )
            ):
                # Stop if we have reached the screenshot_num
                if idx >= screenshot_num:
                    break

                if page.locator('[data-testid="content-gate"]').is_visible():
                    page.locator('[data-testid="content-gate"] button').click()

                page.goto(f'https://reddit.com{comment["comment_url"]}', timeout=0)

                # translate code

                if settings.config["reddit"]["thread"]["post_lang"]:
                    comment_tl = ts.google(
                        comment["comment_body"],
                        to_language=settings.config["reddit"]["thread"]["post_lang"],
                    )
                    page.evaluate(
                        '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > div[data-testid="comment"] > div`).textContent = tl_content',
                        [comment_tl, comment["comment_id"]],
                    )
                try:
                    page.locator(f"#t1_{comment['comment_id']}").screenshot(
                        path=f"assets/temp/{reddit_id}/png/comment_{idx}.png"
                    )
                except TimeoutError:
                    del reddit_object["comments"]
                    screenshot_num += 1
                    print("TimeoutError: Skipping screenshot...")
                    continue

        # close browser instance when we are done using it
        browser.close()



    print_substep("Screenshots downloaded Successfully.", style="bold green")