from asyncio import as_completed

from pyppeteer import launch
from pyppeteer.page import Page as PageCls
from pyppeteer.browser import Browser as BrowserCls
from pyppeteer.element_handle import ElementHandle as ElementHandleCls
from pyppeteer.errors import TimeoutError as BrowserTimeoutError

from pathlib import Path
from typing import Dict
from utils import settings

from rich.progress import track
import translators as ts
from utils.console import print_step, print_substep

from attr import attrs, attrib
from attr.validators import instance_of, optional
from typing import TypeVar, Optional, Callable, Union

_function = TypeVar("_function", bound=Callable[..., object])
_exceptions = TypeVar("_exceptions", bound=Optional[Union[type, tuple, list]])


@attrs
class ExceptionDecorator:
    """
    Decorator factory for catching exceptions and writing logs
    """
    exception: Optional[_exceptions] = attrib(default=None)
    __default_exception: _exceptions = attrib(default=BrowserTimeoutError)

    def __attrs_post_init__(self):
        if not self.exception:
            self.exception = self.__default_exception

    def __call__(
            self,
            func: _function,
    ):
        async def wrapper(*args, **kwargs):
            try:
                obj_to_return = await func(*args, **kwargs)
                return obj_to_return
            except Exception as caughtException:
                import logging

                logger = logging.getLogger("webdriver_log")
                logger.setLevel(logging.ERROR)
                handler = logging.FileHandler(".webdriver.log", mode="a+", encoding="utf-8")
                logger.addHandler(handler)

                if isinstance(self.exception, type):
                    if not type(caughtException) == self.exception:
                        logger.error(f"unexpected error - {caughtException}")
                else:
                    if not type(caughtException) in self.exception:
                        logger.error(f"unexpected error - {caughtException}")

        return wrapper


def catch_exception(
        func: Optional[_function],
        exception: Optional[_exceptions] = None,
) -> Union[ExceptionDecorator, _function]:
    """
    Decorator for catching exceptions and writing logs

    Args:
        func: Function to be decorated
        exception: Expected exception(s)
    Returns:
        Decorated function
    """
    exceptor = ExceptionDecorator(exception)
    if func:
        exceptor = exceptor(func)
    return exceptor


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
    browser: Optional[BrowserCls] = attrib(
        validator=optional(instance_of(BrowserCls)),
        default=None,
        kw_only=True,
    )

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
    @catch_exception
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

    @catch_exception
    async def click(
            self,
            page_instance: Optional[PageCls] = None,
            xpath: Optional[str] = None,
            find_options: Optional[dict] = None,
            options: Optional[dict] = None,
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

    @catch_exception
    async def screenshot(
            self,
            page_instance: Optional[PageCls] = None,
            xpath: Optional[str] = None,
            options: Optional[dict] = None,
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
    """
    reddit_object: dict
    screenshot_idx: list

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
            "//*[contains(@class, 'header-user-dropdown')]",
            {"timeout": 5000},
        )

        # It's normal not to find it, sometimes there is none :shrug:
        await self.click(
            page_instance,
            "//*[contains(text(), 'Settings')]/ancestor::button[1]",
            {"timeout": 5000},
        )

        await self.click(
            page_instance,
            "//*[contains(text(), 'Dark Mode')]/ancestor::button[1]",
            {"timeout": 5000},
        )

        # Closes settings
        await self.click(
            page_instance,
            "//*[contains(@class, 'header-user-dropdown')]",
            {"timeout": 5000},
        )

    async def __close_nsfw(
            self,
            page_instance: PageCls
    ) -> None:
        from asyncio import ensure_future

        print_substep("Post is NSFW. You are spicy...")
        # To await indirectly reload
        navigation = ensure_future(page_instance.waitForNavigation())

        # Triggers indirectly reload
        await self.click(
            page_instance,
            '//button[text()="Yes"]',
            {"timeout": 5000},
        )

        # Await reload
        await navigation

        await (await self.find_xpath(
            page_instance,
            '//button[text()="Click to see nsfw"]',
            {"timeout": 5000},
        )).click()

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
        await comment_page.goto(f'https://reddit.com{comment_obj["comment_url"]}')

        # Translates submission' comment
        if settings.config["reddit"]["thread"]["post_lang"]:
            comment_tl = ts.google(
                comment_obj["comment_body"],
                to_language=settings.config["reddit"]["thread"]["post_lang"],
            )
            await comment_page.evaluate(
                f'([tl_content, tl_id]) => document.querySelector(`#t1_{comment_obj["comment_id"]} > div:nth-child(2) '
                f'> div > div[data-testid="comment"] > div`).textContent = {comment_tl}',
            )

        await self.screenshot(
            comment_page,
            f'//*[contains(@id, \'t1_{comment_obj["comment_id"]}\')]',
            {"path": f"assets/temp/png/comment_{filename_idx}.png"},
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
        await reddit_main.goto(self.reddit_object["thread_url"])

        if settings.config["settings"]["theme"] == "dark":
            await self.__dark_theme(reddit_main)

        if self.reddit_object["is_nsfw"]:
            # This means the post is NSFW and requires to click the proceed button.
            await self.__close_nsfw(reddit_main)

        # Translates submission title
        if settings.config["reddit"]["thread"]["post_lang"]:
            print_substep("Translating post...")
            texts_in_tl = ts.google(
                self.reddit_object["thread_title"],
                to_language=settings.config["reddit"]["thread"]["post_lang"],
            )

            await reddit_main.evaluate(
                "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > "
                "div').textContent = tl_content",
                texts_in_tl,
            )
        else:
            print_substep("Skipping translation...")

        async_tasks_primary = [
            self.__collect_comment(self.reddit_object["comments"][idx], idx) for idx in
            self.screenshot_idx
        ]

        async_tasks_primary.append(
            self.screenshot(
                reddit_main,
                f'//*[contains(@id, \'t3_{self.reddit_object["thread_id"]}\')]',
                {"path": "assets/temp/png/title.png"},
            )
        )

        # Lots of tabs - lots of memory
        # chunk needed to minimize memory required
        def chunks(lst, n):
            """Yield successive n-sized chunks from list."""
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        for idx, chunked_tasks in enumerate(
                [chunk for chunk in chunks(async_tasks_primary, 10)],
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
