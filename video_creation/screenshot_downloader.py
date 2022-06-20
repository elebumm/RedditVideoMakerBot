import json
from os import getenv
import os
from pathlib import Path

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright, ViewportSize
from rich.progress import track

from utils.console import print_step, print_substep
import json
from rich.console import Console

import translators as ts
from PIL import Image, ImageDraw, ImageFont
import textwrap

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

        page.locator('[data-test-id="post-content"]').screenshot(
            path="assets/temp/png/title.png"
        )

        # translate code

        if getenv("POSTLANG"):
            print_substep("Translating post...")
            texts_in_tl = ts.google(reddit_object["thread_title"], to_language=os.getenv("POSTLANG"))

            img = Image.open("assets/temp/png/title.png")
        
            width = img.size[0] 
            height = img.size[1]

            d1 = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 22)
        
            wrapper = textwrap.TextWrapper(width=60)
            wrapped_str = wrapper.fill(text=texts_in_tl)

            if (getenv("THEME").upper() == "DARK"):
                fillmode = "#1a1a1b"
                textmode = (255, 255, 255)
            else:
                fillmode = "whiite"
                textmode = (0, 0, 0)

            d1.rectangle((7, 25, width - 20, height - 35), fill=fillmode)
            d1.text((10, 30), f"{wrapped_str}", font=font, fill=textmode)            
            img.save("assets/temp/png/title.png")
        else:
            print_substep("Skipping translation...")

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

                if getenv("POSTLANG"):
                    img_comment = Image.open(f"assets/temp/png/comment_{idx}.png")
                    width2 = img_comment.size[0] 
                    height2 = img_comment.size[1]
            
                    comment_tl = ts.google(comment["comment_body"], to_language=os.getenv("POSTLANG"))
        
                    wrapper1 = textwrap.TextWrapper(width=78)
                    wrapped_str1 = wrapper1.fill(text=comment_tl)

                    d2 = ImageDraw.Draw(img_comment)
                    font_comment = ImageFont.truetype("arial.ttf", 16)

                    if (getenv("THEME").upper() == "DARK"):
                        fillmode1 = "#242426"
                        textmode1 = (255, 255, 255)
                    else:
                        fillmode1 = "#F5F6F6"
                        textmode1 = (0, 0, 0)

                    d2.rectangle((30, 40, width2 - 5, height2 - 35), fill=fillmode1)
                    d2.text((40, 50), f"{wrapped_str1}", font=font_comment, fill=textmode1)            
                    img_comment.save(f"assets/temp/png/comment_{idx}.png")
        print_substep("Screenshots downloaded Successfully.", style="bold green")
