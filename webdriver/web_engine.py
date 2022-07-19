from typing import Union

from webdriver.pyppeteer import RedditScreenshot as Pyppeteer


def screenshot_factory(
        driver: str,
) -> Union[Pyppeteer]:
    """
    Factory for webdriver
    Args:
        driver: (str) Name of a driver

    Returns:
        Webdriver instance
    """
    web_drivers = {
        "pyppeteer": Pyppeteer,
        "playwright": None,
    }

    return web_drivers[driver]
