from asyncio import as_completed

from pathlib import Path
from typing import Dict

from utils import settings

from pyppeteer import launch
from pyppeteer.page import Page as PageCls
from pyppeteer.browser import Browser as BrowserCls
from pyppeteer.element_handle import ElementHandle as ElementHandleCls
from pyppeteer.errors import TimeoutError as BrowserTimeoutError

from rich.progress import track
import translators as ts

from utils.console import print_step, print_substep

from attr import attrs, attrib
from typing import TypeVar, Optional, Callable, Union

_function = TypeVar('_function', bound=Callable[..., object])
_exceptions = TypeVar('_exceptions', bound=Optional[Union[type, tuple, list]])


@attrs
class ExceptionDecorator:
    __exception: Optional[_exceptions] = attrib(default=None)
    __default_exception: _exceptions = attrib(default=BrowserTimeoutError)

    def __attrs_post_init__(self):
        if not self.__exception:
            self.__exception = self.__default_exception

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

                if isinstance(self.__exception, type):
                    if not type(caughtException) == self.__exception:
                        logging.basicConfig(filename='.webdriver.log', filemode='w', encoding='utf-8',
                                            level=logging.DEBUG)
                        logging.error(f'unexpected error - {caughtException}')
                else:
                    if not type(caughtException) in self.__exception:
                        logging.error(f'unexpected error - {caughtException}')

        return wrapper


def catch_exception(
        func: Optional[_function],
        exception: Optional[_exceptions] = None,
) -> ExceptionDecorator | _function:
    exceptor = ExceptionDecorator(exception)
    if func:
        exceptor = exceptor(func)
    return exceptor


@attrs
class Browser:
    # default_Viewport: dict = attrib(validator=instance_of(dict), default=dict())
    #
    # def __attrs_post_init__(self):
    #     if self.default_Viewport.__len__() == 0:
    #         self.default_Viewport['isLandscape'] = True

    async def get_browser(
            self,
    ) -> BrowserCls:
        return await launch()

    async def close_browser(
            self,
            browser: BrowserCls
    ) -> None:
        await browser.close()


class Wait:
    @staticmethod
    @catch_exception
    async def find_xpath(
            page_instance: PageCls,
            xpath: Optional[str] = None,
            options: Optional[dict] = None,
    ) -> 'ElementHandleCls':
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
        if not el:
            el = await self.find_xpath(page_instance, xpath, find_options)
        if options:
            await el.screenshot(options)
        else:
            await el.screenshot()


@attrs(auto_attribs=True)
class Reddit(Browser, Wait):
    """
    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """
    reddit_object: dict
    screenshot_num: int = attrib()

    @screenshot_num.validator
    def validate_screenshot_num(self, attribute, value):
        if value <= 0:
            raise ValueError('Check screenshot_num in config')

    async def dark_theme(
            self,
            page_instance: PageCls,
    ) -> None:
        """
        Enables dark theme in Reddit
        """

        await self.click(
            page_instance,
            '//*[contains(@class, \'header-user-dropdown\')]',
            {'timeout': 5000},
        )

        # It's normal not to find it, sometimes there is none :shrug:
        await self.click(
            page_instance,
            '//*[contains(text(), \'Settings\')]/ancestor::button[1]',
            {'timeout': 5000},
        )

        await self.click(
            page_instance,
            '//*[contains(text(), \'Dark Mode\')]/ancestor::button[1]',
            {'timeout': 5000},
        )

        # Closes settings
        await self.click(
            page_instance,
            '//*[contains(@class, \'header-user-dropdown\')]',
            {'timeout': 5000},
        )

    async def download_screenshots(
            self,
            browser: BrowserCls

    ):
        """
        Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png
        """
        print_step('Downloading screenshots of reddit posts...')

        # ! Make sure the reddit screenshots folder exists
        Path('assets/temp/png').mkdir(parents=True, exist_ok=True)

        print_substep('Launching Headless Browser...')

        # Get the thread screenshot
        reddit_main = await browser.newPage()
        await reddit_main.goto(self.reddit_object['thread_url'])

        if settings.config['settings']['theme'] == 'dark':
            await self.dark_theme(reddit_main)

        if self.reddit_object['is_nsfw']:
            # This means the post is NSFW and requires to click the proceed button.

            print_substep('Post is NSFW. You are spicy...')
            await self.click(
                reddit_main,
                '//button[contains(text(), \'Yes\')]',
                {'timeout': 5000},
            )

            await self.click(
                reddit_main,
                '//button[contains(text(), \'nsfw\')]',
                {'timeout': 5000},
            )

        # translate code

        if settings.config['reddit']['thread']['post_lang']:
            print_substep('Translating post...')
            texts_in_tl = ts.google(
                self.reddit_object['thread_title'],
                to_language=settings.config['reddit']['thread']['post_lang'],
            )

            await reddit_main.evaluate(
                "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > "
                "div').textContent = tl_content",
                texts_in_tl,
            )
        else:
            print_substep("Skipping translation...")

        await self.screenshot(
            reddit_main,
            f'//*[contains(@id, \'t3_{self.reddit_object["thread_id"]}\')]',
            {'path': f'assets/temp/png/title.png'},
        )

        async def collect_comment(
                comment_obj: dict,
                filename_idx: int,
        ):
            comment_page = await browser.newPage()
            await comment_page.goto(f'https://reddit.com{comment_obj["comment_url"]}')

            # translate code
            if settings.config["reddit"]["thread"]["post_lang"]:
                comment_tl = ts.google(
                    comment_obj["comment_body"],
                    to_language=settings.config["reddit"]["thread"]["post_lang"],
                )
                await comment_page.evaluate(
                    '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > div['
                    'data-testid="comment"] > div`).textContent = tl_content',
                    [comment_tl, comment_obj["comment_id"]],
                )

            await self.screenshot(
                comment_page,
                f'//*[contains(@id, \'t1_{comment_obj["comment_id"]}\')]',
                {'path': f'assets/temp/png/comment_{filename_idx}.png'},
            )

        async_tasks_primary = [
            collect_comment(comment, idx) for idx, comment in
            enumerate(self.reddit_object['comments'])
            if idx < self.screenshot_num
        ]

        for task in track(
                as_completed(async_tasks_primary),
                description='Downloading screenshots...',
                total=async_tasks_primary.__len__(),
        ):
            await task

        print_substep('Screenshots downloaded Successfully.', style='bold green')
