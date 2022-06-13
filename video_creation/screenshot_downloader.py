from playwright.sync_api import sync_playwright, ViewportSize
from pathlib import Path
from rich.progress import track
from utils.console import print_step, print_substep
import json
import translators as ts
from PIL import Image, ImageDraw, ImageFont
import textwrap

def download_screenshots_of_reddit_posts(reddit_object, screenshot_num, theme, target_lang):
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

        texts_in_tl = ts.bing(reddit_object["thread_title"], to_language=target_lang)

        page.locator('[data-test-id="post-content"]').screenshot(
            path="assets/png/title.png"
        )

        # rewrite the title in target language
        img = Image.open("assets/png/title.png")
        
        width = img.size[0] 
        height = img.size[1]

        d1 = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 22)
        
        w, h = font.getsize(new_str)
        d1.rectangle((9, 25, 20 + width, 55 + h), fill='white')
        d1.text((10, 25), f"{new_str}", font=font, fill=(0, 0, 0))            
        img.save("assets/png/title.png")

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

            # translating the comments
            img_comment = Image.open(f"assets/png/comment_{idx}.png")
            width = img_comment.size[0] 
            height = img_comment.size[1]
            
            comment_tl = ts.bing(comment["comment_body"], to_language=target_lang)
        
            wrapper = textwrap.TextWrapper(width=78)
            wrapped_str = wrapper.fill(text=comment_tl)

            d2 = ImageDraw.Draw(img_comment)
            font_comment = ImageFont.truetype("arial.ttf", 16)
            
            d2.rectangle((9, 45, width - 10, height - 35), fill='#F5F6F6')
            d2.text((10, 48), f"{wrapped_str}", font=font_comment, fill=(0, 0, 0))            
            img_comment.save(f"assets/png/comment_{idx}.png")

        print_substep("Screenshots downloaded Successfully.",
                      style="bold green")
