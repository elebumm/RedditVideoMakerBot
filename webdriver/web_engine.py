from typing import Union

from webdriver.pyppeteer import RedditScreenshot as Pyppeteer
from webdriver.playwright import RedditScreenshot as Playwright


def screenshot_factory(
        driver: str,
) -> Union[type(Pyppeteer), type(Playwright)]:
    """
    Factory for webdriver
    Args:
        driver: (str) Name of a driver

    Returns:
        Webdriver instance
    """
    web_drivers = {
        "pyppeteer": Pyppeteer,
        "playwright": Playwright,
    }

    return web_drivers[driver]
