import json
from os import getenv
from pathlib import Path

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright, ViewportSize
from rich.progress import track

from utils.console import print_step, print_substep
import json
from rich.console import Console

console = Console()

storymode = False


def download_screenshots_of_reddit_posts(reddit_object, screenshot_num):
    """Downloads screenshots of reddit posts as they are seen on the web.
    Args:
            reddit_object: The Reddit Object you received in askreddit.py
            screenshot_num: The number of screenshots you want to download.
    """
    print_step("Downloading screenshots of reddit posts...")

    # ! Make sure the reddit screenshots folder exists
    Path("assets/temp/png").mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        print_substep("Launching Headless Browser...")

        browser = p.chromium.launch()
        context = browser.new_context()

        if getenv("THEME").upper() == "DARK":
            cookie_file = open("./video_creation/data/cookie-dark-mode.json")
        else:
            cookie_file = open("./video_creation/data/cookie-light-mode.json")
        cookies = json.load(cookie_file)
        context.add_cookies(cookies)  # load preference cookies
        # Get the thread screenshot
        page = context.new_page()
        page.goto(reddit_object["thread_url"], timeout=0)
        page.set_viewport_size(ViewportSize(width=1920, height=1080))
        if page.locator('[data-testid="content-gate"]').is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            print_substep("Post is NSFW. You are spicy...")
            page.locator('[data-testid="content-gate"] button').click()
            page.locator(
                '[data-click-id="text"] button'
            ).click()  # Remove "Click to see nsfw" Button in Screenshot

        page.locator('[data-test-id="post-content"]').screenshot(path="assets/temp/png/title.png")
        if storymode:
            page.locator('[data-click-id="text"]').screenshot(
                path="assets/temp/png/story_content.png"
            )
        else:
            for idx, comment in track(
                enumerate(reddit_object["comments"]), "Downloading screenshots..."
            ):

                # Stop if we have reached the screenshot_num
                if idx >= screenshot_num:
                    break

                if page.locator('[data-testid="content-gate"]').is_visible():
                    page.locator('[data-testid="content-gate"] button').click()

                page.goto(f'https://reddit.com{comment["comment_url"]}', timeout=0)
                page.locator(f"#t1_{comment['comment_id']}").screenshot(
                    path=f"assets/temp/png/comment_{idx}.png"
                )
        print_substep("Screenshots downloaded Successfully.", style="bold green")
