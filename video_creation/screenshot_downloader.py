import json
import re
from pathlib import Path
from typing import Dict

import translators as ts
from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright
from rich.progress import track

from utils import settings
from utils.console import print_step, print_substep
from utils.imagenarator import imagemaker

# do not remove the above line


def get_screenshots_of_reddit_posts(reddit_object: dict, screenshot_num: int):
    """Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """

    print_step("Downloading screenshots of reddit posts...")

    id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])

    # ! Make sure the reddit screenshots folder exists
    Path(f"assets/temp/{id}/png").mkdir(parents=True, exist_ok=True)

    def download(cookie_file, num=None):
        screenshot_num = num
        with sync_playwright() as p:
            print_substep("Launching Headless Browser...")

            browser = p.chromium.launch()  # headless=False #to check for chrome view
            context = browser.new_context()

            cookies = json.load(cookie_file)

            context.add_cookies(cookies)  # load preference cookies
            # Get the thread screenshot
            page = context.new_page()
            page.goto(reddit_object["thread_url"], timeout=0)
            page.set_viewport_size(ViewportSize(width=settings.config["settings"]["vwidth"], height=1920))
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

            if settings.config["reddit"]["thread"]["post_lang"]:
                print_substep("Translating post...")
                texts_in_tl = ts.google(
                    reddit_object["thread_title"],
                    to_language=settings.config["reddit"]["thread"]["post_lang"],
                )

                page.evaluate(
                    "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > div').textContent = tl_content",
                    texts_in_tl,
                )
            else:
                print_substep("Skipping translation...")
            postcontentpath = f"assets/temp/{id}/png/title.png"
            page.locator('[data-test-id="post-content"]').screenshot(
                path=postcontentpath
            )

            if settings.config["settings"]["storymode"]:

                try:  # new change
                    page.locator('[data-click-id="text"]').first.screenshot(
                        path=f"assets/temp/{id}/png/story_content.png"
                    )
                except:
                    exit
            if not settings.config["settings"]["storymode"]:
                for idx, comment in enumerate(
                    track(reddit_object["comments"], "Downloading screenshots...")
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
                            to_language=settings.config["reddit"]["thread"][
                                "post_lang"
                            ],
                        )
                        page.evaluate(
                            '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > div[data-testid="comment"] > div`).textContent = tl_content',
                            [comment_tl, comment["comment_id"]],
                        )
                    try:
                        page.locator(f"#t1_{comment['comment_id']}").screenshot(
                            path=f"assets/temp/{id}/png/comment_{idx}.png"
                        )
                    except TimeoutError:
                        del reddit_object["comments"]
                        screenshot_num -= 1
                        print("TimeoutError: Skipping screenshot...")
                        continue
        print_substep("Screenshots downloaded Successfully.", style="bold green")

    # story=False
    theme = settings.config["settings"]["theme"]
    if theme == "dark":
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
    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 1:
            # for idx,item in enumerate(reddit_object["thread_post"]):
            imagemaker(theme=bgcolor, reddit_obj=reddit_object, txtclr=txtcolor)

    if (
        settings.config["settings"]["storymodemethod"] == 0
        or not settings.config["settings"]["storymode"]
    ):
        download(cookie_file, screenshot_num)
