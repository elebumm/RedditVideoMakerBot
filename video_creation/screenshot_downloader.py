import json
import re
from pathlib import Path
from typing import Dict, Final

import translators
from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright
from rich.progress import track

from utils import settings
from utils.console import print_step, print_substep
from utils.imagenarator import imagemaker
from utils.playwright import clear_cookie_by_name

from utils.videos import save_data

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

    # set the theme and disable non-essential cookies
    if settings.config["settings"]["theme"] == "dark":
        cookie_file = open("./video_creation/data/cookie-dark-mode.json", encoding="utf-8")
        bgcolor = (33, 33, 36, 255)
        txtcolor = (240, 240, 240)
        transparent = False
    elif settings.config["settings"]["theme"] == "transparent":
        if storymode:
            # Transparent theme
            bgcolor = (0, 0, 0, 0)
            txtcolor = (255, 255, 255)
            transparent = True
            cookie_file = open("./video_creation/data/cookie-dark-mode.json", encoding="utf-8")
        else:
            # Switch to dark theme
            cookie_file = open("./video_creation/data/cookie-dark-mode.json", encoding="utf-8")
            bgcolor = (33, 33, 36, 255)
            txtcolor = (240, 240, 240)
            transparent = False
    else:
        cookie_file = open("./video_creation/data/cookie-light-mode.json", encoding="utf-8")
        bgcolor = (255, 255, 255, 255)
        txtcolor = (0, 0, 0)
        transparent = False
    if storymode and settings.config["settings"]["storymodemethod"] == 1:
        # for idx,item in enumerate(reddit_object["thread_post"]):
        print_substep("Generating images...")
        return imagemaker(
            theme=bgcolor,
            reddit_obj=reddit_object,
            txtclr=txtcolor,
            transparent=transparent,
        )

    screenshot_num: int
    with sync_playwright() as p:
        print_substep("Launching Headless Browser...")

        browser = p.chromium.launch(
            headless=True
        )  # headless=False will show the browser for debugging purposes
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
        cookies = json.load(cookie_file)
        cookie_file.close()

        context.add_cookies(cookies)  # load preference cookies

        # Login to Reddit
        print_substep("Logging in to Reddit...")
        page = context.new_page()
        page.goto("https://www.reddit.com/login", timeout=0)
        page.set_viewport_size(ViewportSize(width=1920, height=1080))
        page.wait_for_load_state()

        page.locator('[name="username"]').fill(settings.config["reddit"]["creds"]["username"])
        page.locator('[name="password"]').fill(settings.config["reddit"]["creds"]["password"])
        page.locator("button[class$='m-full-width']").click()
        page.wait_for_timeout(5000)

        login_error_div = page.locator(".AnimatedForm__errorMessage").first
        if login_error_div.is_visible():
            login_error_message = login_error_div.inner_text()
            if login_error_message.strip() == "":
                # The div element is empty, no error
                pass
            else:
                # The div contains an error message
                print_substep(
                    "Your reddit credentials are incorrect! Please modify them accordingly in the config.toml file.",
                    style="red",
                )
                exit()
        else:
            pass

        page.wait_for_load_state()
        # Handle the redesign
        # Check if the redesign optout cookie is set
        if page.locator("#redesign-beta-optin-btn").is_visible():
            # Clear the redesign optout cookie
            clear_cookie_by_name(context, "redesign_optout")
            # Reload the page for the redesign to take effect
            page.reload()
        # Get the thread screenshot
        page.goto(reddit_object["thread_url"], timeout=0)
        page.set_viewport_size(ViewportSize(width=W, height=H))
        page.wait_for_load_state()
        page.wait_for_timeout(5000)

        if page.locator(
            "#t3_12hmbug > div > div._3xX726aBn29LDbsDtzr_6E._1Ap4F5maDtT1E1YuCiaO0r.D3IL3FD0RFy_mkKLPwL4 > div > div > button"
        ).is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            print_substep("Post is NSFW. You are spicy...")
            page.locator(
                "#t3_12hmbug > div > div._3xX726aBn29LDbsDtzr_6E._1Ap4F5maDtT1E1YuCiaO0r.D3IL3FD0RFy_mkKLPwL4 > div > div > button"
            ).click()
            page.wait_for_load_state()  # Wait for page to fully load

            # translate code
        if page.locator(
            "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
        ).is_visible():
            page.locator(
                "#SHORTCUT_FOCUSABLE_DIV > div:nth-child(7) > div > div > div > header > div > div._1m0iFpls1wkPZJVo38-LSh > button > i"
            ).click()  # Interest popup is showing, this code will close it

        if lang:
            print_substep("Translating post...")
            texts_in_tl = translators.translate_text(
                reddit_object["thread_title"],
                to_language=lang,
                translator="google",
            )

            page.evaluate(
                "tl_content => document.querySelector('[data-adclicklocation=\"title\"] > div > div > h1').textContent = tl_content",
                texts_in_tl,
            )
        else:
            print_substep("Skipping translation...")

        postcontentpath = f"assets/temp/{reddit_id}/png/title.png"
        try:
            if settings.config["settings"]["zoom"] != 1:
                # store zoom settings
                zoom = settings.config["settings"]["zoom"]
                # zoom the body of the page
                page.evaluate("document.body.style.zoom=" + str(zoom))
                # as zooming the body doesn't change the properties of the divs, we need to adjust for the zoom
                location = page.locator('[data-test-id="post-content"]').bounding_box()
                for i in location:
                    location[i] = float("{:.2f}".format(location[i] * zoom))
                page.screenshot(clip=location, path=postcontentpath)
            else:
                page.locator('[data-test-id="post-content"]').screenshot(path=postcontentpath)
        except Exception as e:
            print_substep("Something went wrong!", style="red")
            resp = input(
                "Something went wrong with making the screenshots! Do you want to skip the post? (y/n) "
            )

            if resp.casefold().startswith("y"):
                save_data("", "", "skipped", reddit_id, "")
                print_substep(
                    "The post is successfully skipped! You can now restart the program and this post will skipped.",
                    "green",
                )

            resp = input("Do you want the error traceback for debugging purposes? (y/n)")
            if not resp.casefold().startswith("y"):
                exit()

            raise e

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
                    comment_tl = translators.translate_text(
                        comment["comment_body"],
                        translator="google",
                        to_language=settings.config["reddit"]["thread"]["post_lang"],
                    )
                    page.evaluate(
                        '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > div[data-testid="comment"] > div`).textContent = tl_content',
                        [comment_tl, comment["comment_id"]],
                    )
                try:
                    if settings.config["settings"]["zoom"] != 1:
                        # store zoom settings
                        zoom = settings.config["settings"]["zoom"]
                        # zoom the body of the page
                        page.evaluate("document.body.style.zoom=" + str(zoom))
                        # scroll comment into view
                        page.locator(f"#t1_{comment['comment_id']}").scroll_into_view_if_needed()
                        # as zooming the body doesn't change the properties of the divs, we need to adjust for the zoom
                        location = page.locator(f"#t1_{comment['comment_id']}").bounding_box()
                        for i in location:
                            location[i] = float("{:.2f}".format(location[i] * zoom))
                        page.screenshot(
                            clip=location,
                            path=f"assets/temp/{reddit_id}/png/comment_{idx}.png",
                        )
                    else:
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
