from playwright.sync_api import sync_playwright, ViewportSize
from pathlib import Path
from rich.progress import track
from utils.console import print_step, print_substep
import json


def download_screenshots_of_reddit_posts(reddit_object, screenshot_num, theme):
    """Downloads screenshots of reddit posts as they are seen on the web.

    Args:
        reddit_object: The Reddit Object you received in askreddit.py
        screenshot_num: The number of screenshots you want to download.
    """
    print_step("Downloading Screenshots of Reddit Posts 📷")

    # ! Make sure the reddit screenshots folder exists
    Path("assets/png").mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        print_substep("Launching Headless Browser...")

        browser = p.chromium.launch()
        context = browser.new_context()

        if theme.casefold() == "dark":
            cookie_file = open('video_creation/cookies.json')
            cookies = json.load(cookie_file)
            context.add_cookies(cookies)

        # Get the thread screenshot
        page = context.new_page()
        page.goto(reddit_object["thread_url"])
        page.set_viewport_size(ViewportSize(width=1920, height=1080))
        if page.locator('[data-testid="content-gate"]').is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            print_substep("Post is NSFW. You are spicy...")
            page.locator('[data-testid="content-gate"] button').click()

        page.locator('[data-test-id="post-content"]').screenshot(
            path="assets/png/title.png"
        )

        for idx, comment in track(
            enumerate(reddit_object["comments"]), "Downloading screenshots..."
        ):

            # Stop if we have reached the screenshot_num
            if idx >= screenshot_num:
                break

            if page.locator('[data-testid="content-gate"]').is_visible():
                page.locator('[data-testid="content-gate"] button').click()

            page.goto(f'https://reddit.com{comment["comment_url"]}')
            page.locator(f"#t1_{comment['comment_id']}").screenshot(
                path=f"assets/png/comment_{idx}.png"
            )

        print_substep("Screenshots downloaded Successfully.",
                      style="bold green")
