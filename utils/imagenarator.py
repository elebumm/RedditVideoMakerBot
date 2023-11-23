import re
import textwrap
import os
import json
from typing import Final

from utils import settings

from PIL import Image, ImageDraw, ImageFont
from rich.progress import track
from TTS.engine_wrapper import process_text
from utils.console import print_substep
from utils.videos import save_data


from pathlib import Path

import translators
from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright
from rich.progress import track

from utils import settings
from utils.console import print_substep
from utils.playwright import clear_cookie_by_name

from utils.videos import save_data


def get_title_screenshot(reddit_object: dict):
    W: Final[int] = int(settings.config["settings"]["resolution_w"])
    H: Final[int] = int(settings.config["settings"]["resolution_h"])
    lang: Final[str] = settings.config["reddit"]["thread"]["post_lang"]

    reddit_id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
    # ! Make sure the reddit screenshots folder exists
    Path(f"assets/temp/{reddit_id}/png").mkdir(parents=True, exist_ok=True)

    if settings.config["settings"]["theme"] == "dark":
        cookie_file = open("./video_creation/data/cookie-dark-mode.json", encoding="utf-8")
    elif settings.config["settings"]["theme"] == "transparent":
        cookie_file = open("./video_creation/data/cookie-dark-mode.json", encoding="utf-8")
    else:
        cookie_file = open("./video_creation/data/cookie-light-mode.json", encoding="utf-8")

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
        page.evaluate(
            "document.querySelector('[data-adclicklocation=\"media\"]').style.display = 'none'"
        )

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

def load_text_replacements():
    text_replacements = {}
    # Load background videos
    with open("./utils/text_replacements.json") as json_file:
        text_replacements = json.load(json_file)
    del text_replacements["__comment"]
    return text_replacements

def perform_text_replacements(text):
    updated_text = text
    for replacement in text_replacements['text-and-audio']:
        regex_escaped_word=re.escape(replacement[0])
        compiled = re.compile(r"\b{}\b".format(regex_escaped_word), re.IGNORECASE)
        updated_text = compiled.sub(replacement[1], updated_text)
    for replacement in text_replacements['text-only']:
        compiled = re.compile(r"\b{}\b".format(regex_escaped_word), re.IGNORECASE)
        updated_text = compiled.sub(replacement[1], updated_text)
    return updated_text


def draw_multiple_line_text(
    image, text, font, text_color, padding, wrap=50, transparent=False
) -> None:
    """
    Draw multiline text over given image
    """
    draw = ImageDraw.Draw(image)
    Fontperm = font.getsize(text)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    y = (image_height / 2) - (((Fontperm[1] + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
    for line in lines:
        line_width, line_height = font.getsize(line)
        if transparent:
            shadowcolor = "black"
            for i in range(1, 5):
                draw.text(
                    ((image_width - line_width) / 2 - i, y - i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 + i, y - i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 - i, y + i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 + i, y + i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
        draw.text(((image_width - line_width) / 2, y), line, font=font, fill=text_color)
        y += line_height + padding


def imagemaker(theme, reddit_obj: dict, txtclr, transparent=False) -> None:
    """
    Render Images for video
    """
    title = process_text(perform_text_replacements(reddit_obj["thread_title"]), False)
    texts = reddit_obj["thread_post"]
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    if transparent:
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), int(settings.config["settings"]["text_size"])) # changed
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), int(settings.config["settings"]["text_size"])) # changed
    else:
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), int(settings.config["settings"]["text_size"]))  # for title # changed
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), int(settings.config["settings"]["text_size"])) # changed

    size = (int(settings.config["settings"]["resolution_w"]), int(settings.config["settings"]["resolution_h"]))


    if bool(settings.config['settings']['title_screenshot']):
        get_title_screenshot(reddit_obj)
    else:
        image = Image.new("RGBA", size, theme)
        # for title
        draw_multiple_line_text(image, perform_text_replacements(title), tfont, txtclr, int(settings.config["settings"]["text_padding"]), wrap=int(settings.config["settings"]["text_wrap"]), transparent=transparent)
        image.save(f"assets/temp/{id}/png/title.png")

    for idx, text in track(enumerate(texts), "💬 Rendering captions...", total=len(texts)):
        image = Image.new("RGBA", size, theme)
        text = process_text(text, False)
        draw_multiple_line_text(image, perform_text_replacements(text), font, txtclr, int(settings.config["settings"]["text_padding"]), wrap=int(settings.config["settings"]["text_wrap"]), transparent=transparent)
        image.save(f"assets/temp/{id}/png/img{idx}.png")
    print_substep("Captions rendered successfully!", style="bold green")

text_replacements = load_text_replacements()