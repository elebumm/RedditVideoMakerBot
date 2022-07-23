from asyncio import as_completed

from pyppeteer import launch
from pyppeteer.page import Page as PageCls
from pyppeteer.browser import Browser as BrowserCls
from pyppeteer.element_handle import ElementHandle as ElementHandleCls
from pyppeteer.errors import TimeoutError as BrowserTimeoutError

from pathlib import Path
from utils import settings
from utils.console import print_step, print_substep
from rich.progress import track
import translators as ts

from attr import attrs, attrib
from attr.validators import instance_of
from typing import Optional

import webdriver.common as common

common.default_exception = BrowserTimeoutError


@attrs
class Browser:
    """
    Args:
        default_Viewport (dict):Pyppeteer Browser default_Viewport options
        browser (BrowserCls): Pyppeteer Browser instance
    """
    default_Viewport: dict = attrib(
        validator=instance_of(dict),
        default={
            # 9x21 to see long posts
            "defaultViewport": {
                "width": 500,
                "height": 1200,
            },
        },
        kw_only=True,
    )
    browser: BrowserCls

    async def get_browser(
            self,
    ) -> None:
        """
        Creates Pyppeteer browser
        """
        self.browser = await launch(self.default_Viewport)

    async def close_browser(
            self,
    ) -> None:
        """
        Closes Pyppeteer browser
        """
        await self.browser.close()


class Wait:
    @staticmethod
    @common.catch_exception
    async def find_xpath(
            page_instance: PageCls,
            xpath: Optional[str] = None,
            options: Optional[dict] = None,
    ) -> 'ElementHandleCls':
        """
        Explicitly finds element on the page

        Args:
            page_instance: Pyppeteer page instance
            xpath: xpath query
            options: Pyppeteer waitForXPath parameters

        Available options are:

        * ``visible`` (bool): wait for element to be present in DOM and to be
          visible, i.e. to not have ``display: none`` or ``visibility: hidden``
          CSS properties. Defaults to ``False``.
        * ``hidden`` (bool): wait for element to not be found in the DOM or to
          be hidden, i.e. have ``display: none`` or ``visibility: hidden`` CSS
          properties. Defaults to ``False``.
        * ``timeout`` (int|float): maximum time to wait for in milliseconds.
          Defaults to 30000 (30 seconds). Pass ``0`` to disable timeout.
        Returns:
            Pyppeteer element instance
        """
        if options:
            el = await page_instance.waitForXPath(xpath, options=options)
        else:
            el = await page_instance.waitForXPath(xpath)
        return el

    @common.catch_exception
    async def click(
            self,
            page_instance: Optional[PageCls] = None,
            xpath: Optional[str] = None,
            options: Optional[dict] = None,
            *,
            find_options: Optional[dict] = None,
            el: Optional[ElementHandleCls] = None,
    ) -> None:
        """
        Clicks on the element

        Args:
            page_instance: Pyppeteer page instance
            xpath: xpath query
            find_options: Pyppeteer waitForXPath parameters
            options: Pyppeteer click parameters
            el: Pyppeteer element instance
        """
        if not el:
            el = await self.find_xpath(page_instance, xpath, find_options)
        if options:
            await el.click(options)
        else:
            await el.click()

    @common.catch_exception
    async def screenshot(
            self,
            page_instance: Optional[PageCls] = None,
            xpath: Optional[str] = None,
            options: Optional[dict] = None,
            *,
            find_options: Optional[dict] = None,
            el: Optional[ElementHandleCls] = None,
    ) -> None:
        """
        Makes a screenshot of the element

        Args:
            page_instance:  Pyppeteer page instance
            xpath: xpath query
            options: Pyppeteer screenshot parameters
            find_options: Pyppeteer waitForXPath parameters
            el: Pyppeteer element instance
        """
        if not el:
            el = await self.find_xpath(page_instance, xpath, find_options)
        if options:
            await el.screenshot(options)
        else:
            await el.screenshot()


@attrs(auto_attribs=True)
class RedditScreenshot(Browser, Wait):
    """
    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_idx (int): List with indexes of voiced comments
        story_mode (bool): If submission is a story takes screenshot of the story
    """
    reddit_object: dict
    screenshot_idx: list
    story_mode: Optional[bool] = attrib(
        validator=instance_of(bool),
        default=False,
        kw_only=True
    )

    def __attrs_post_init__(
            self,
    ):
        self.post_lang: Optional[bool] = settings.config["reddit"]["thread"]["post_lang"]

    async def __dark_theme(
            self,
            page_instance: PageCls,
    ) -> None:
        """
        Enables dark theme in Reddit

        Args:
            page_instance: Pyppeteer page instance with reddit page opened
        """

        await self.click(
            page_instance,
            "//div[@class='header-user-dropdown']",
            find_options={"timeout": 5000},
        )

        # It's normal not to find it, sometimes there is none :shrug:
        await self.click(
            page_instance,
            "//span[text()='Settings']/ancestor::button[1]",
            find_options={"timeout": 5000},
        )

        await self.click(
            page_instance,
            "//span[text()='Dark Mode']/ancestor::button[1]",
            find_options={"timeout": 5000},
        )

        # Closes settings
        await self.click(
            page_instance,
            "//div[@class='header-user-dropdown']",
            find_options={"timeout": 5000},
        )

    async def __close_nsfw(
            self,
            page_instance: PageCls,
    ) -> None:
        """
        Closes NSFW stuff

        Args:
            page_instance:  Instance of main page
        """

        from asyncio import ensure_future

        print_substep("Post is NSFW. You are spicy...")
        # To await indirectly reload
        navigation = ensure_future(page_instance.waitForNavigation())

        # Triggers indirectly reload
        await self.click(
            page_instance,
            '//button[text()="Yes"]',
            find_options={"timeout": 5000},
        )

        # Await reload
        await navigation

        await self.click(
            page_instance,
            '//button[text()="Click to see nsfw"]',
            find_options={"timeout": 5000},
        )

    async def __collect_comment(
            self,
            comment_obj: dict,
            filename_idx: int,
    ) -> None:
        """
        Makes a screenshot of the comment

        Args:
            comment_obj: prew comment object
            filename_idx: index for the filename
        """
        comment_page = await self.browser.newPage()
        await comment_page.goto(
            f'https://reddit.com{comment_obj["comment_url"]}',
            timeout=0,  # Fix for Navigation TimeoutError
        )

        # Translates submission' comment
        if self.post_lang:
            comment_tl = ts.google(
                comment_obj["comment_body"],
                to_language=self.post_lang,
            )
            await comment_page.evaluate(
                '([comment_id, comment_tl]) => document.querySelector(`#t1_${comment_id} > div:nth-child(2) > div > div[data-testid="comment"] > div`).textContent = comment_tl',  # noqa
                [comment_obj["comment_id"], comment_tl],
            )

        await self.screenshot(
            comment_page,
            f"//div[@id='t1_{comment_obj['comment_id']}']",
            {"path": f"assets/temp/png/comment_{filename_idx}.png"},
        )

    # WIP  TODO test it
    async def __collect_story(
            self,
            main_page: PageCls,
    ):
        # Translates submission text
        if self.post_lang:
            story_tl = ts.google(
                self.reddit_object["thread_post"],
                to_language=self.post_lang,
            )
            split_story_tl = story_tl.split('\n')

            await main_page.evaluate(
                "(split_story_tl) => split_story_tl.map(function(element, i) { return [element, document.querySelectorAll('[data-test-id=\"post-content\"] > [data-click-id=\"text\"] > div > p')[i]]; }).forEach(mappedElement => mappedElement[1].textContent = mappedElement[0])",  # noqa
                split_story_tl,
            )

        await self.screenshot(
            main_page,
            "//div[@data-test-id='post-content']//div[@data-click-id='text']",
            {"path": "assets/temp/png/story_content.png"},
        )

    async def download(
            self,
    ):
        """
        Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png
        """
        print_step("Downloading screenshots of reddit posts...")

        print_substep("Launching Headless Browser...")
        await self.get_browser()

        # ! Make sure the reddit screenshots folder exists
        Path("assets/temp/png").mkdir(parents=True, exist_ok=True)

        # Get the thread screenshot
        reddit_main = await self.browser.newPage()
        await reddit_main.goto(  # noqa
            self.reddit_object["thread_url"],
            timeout=0,  # Fix for Navigation TimeoutError
        )

        if settings.config["settings"]["theme"] == "dark":
            await self.__dark_theme(reddit_main)

        if self.reddit_object["is_nsfw"]:
            # This means the post is NSFW and requires to click the proceed button.
            await self.__close_nsfw(reddit_main)

        # Translates submission title
        if self.post_lang:
            print_substep("Translating post...")
            texts_in_tl = ts.google(
                self.reddit_object["thread_title"],
                to_language=self.post_lang,
            )

            await reddit_main.evaluate(
                f"(texts_in_tl) => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > div').textContent = texts_in_tl",  # noqa
                texts_in_tl,
            )
        else:
            print_substep("Skipping translation...")

        # No sense to move it to common.py
        async_tasks_primary = (  # noqa
            [
                self.__collect_comment(self.reddit_object["comments"][idx], idx) for idx in
                self.screenshot_idx
            ]
            if not self.story_mode
            else [
                self.__collect_story(reddit_main)
            ]
        )

        async_tasks_primary.append(
            self.screenshot(
                reddit_main,
                f"//div[@data-testid='post-container']",
                {"path": "assets/temp/png/title.png"},
            )
        )

        for idx, chunked_tasks in enumerate(
                [chunk for chunk in common.chunks(async_tasks_primary, 10)],
                start=1,
        ):
            chunk_list = async_tasks_primary.__len__() // 10 + (1 if async_tasks_primary.__len__() % 10 != 0 else 0)
            for task in track(
                    as_completed(chunked_tasks),
                    description=f"Downloading comments: Chunk {idx}/{chunk_list}",
                    total=chunked_tasks.__len__(),
            ):
                await task

        print_substep("Comments downloaded Successfully.", style="bold green")
        await self.close_browser()
