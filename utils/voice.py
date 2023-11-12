import re
import sys
import json
import time as pytime
from datetime import datetime
from time import sleep

from requests import Response

from utils import settings
from cleantext import clean

if sys.version_info[0] >= 3:
    from datetime import timezone

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
        compiled = re.compile(re.escape(replacement[0]), re.IGNORECASE)
        updated_text = compiled.sub(replacement[1], updated_text)
    for replacement in text_replacements['audio-only']:
        compiled = re.compile(re.escape(replacement[0]), re.IGNORECASE)
        updated_text = compiled.sub(replacement[1], updated_text)
    return updated_text

def check_ratelimit(response: Response) -> bool:
    """
    Checks if the response is a ratelimit response.
    If it is, it sleeps for the time specified in the response.
    """
    if response.status_code == 429:
        try:
            time = int(response.headers["X-RateLimit-Reset"])
            print(f"Ratelimit hit. Sleeping for {time - int(pytime.time())} seconds.")
            sleep_until(time)
            return False
        except KeyError:  # if the header is not present, we don't know how long to wait
            return False

    return True


def sleep_until(time) -> None:
    """
    Pause your program until a specific end time.
    'time' is either a valid datetime object or unix timestamp in seconds (i.e. seconds since Unix epoch)
    """
    end = time

    # Convert datetime to unix timestamp and adjust for locality
    if isinstance(time, datetime):
        # If we're on Python 3 and the user specified a timezone, convert to UTC and get the timestamp.
        if sys.version_info[0] >= 3 and time.tzinfo:
            end = time.astimezone(timezone.utc).timestamp()
        else:
            zoneDiff = pytime.time() - (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            end = (time - datetime(1970, 1, 1)).total_seconds() + zoneDiff

    # Type check
    if not isinstance(end, (int, float)):
        raise Exception("The time parameter is not a number or datetime object")

    # Now we wait
    while True:
        now = pytime.time()
        diff = end - now

        #
        # Time is up!
        #
        if diff <= 0:
            break
        else:
            # 'logarithmic' sleeping to minimize loop iterations
            sleep(diff / 2)


def sanitize_text(text: str) -> str:
    r"""Sanitizes the text for tts.
        What gets removed:
     - following characters`^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
     - any http or https links

    Args:
        text (str): Text to be sanitized

    Returns:
        str: Sanitized text
    """

    # remove any urls from the text
    regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

    result = re.sub(regex_urls, " ", text)

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%—“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", result)
    result = result.replace("+", "plus").replace("&", "and")

    # emoji removal if the setting is enabled
    if settings.config["settings"]["tts"]["no_emojis"]:
        result = clean(result, no_emoji=True)

    result = perform_text_replacements(result)

    # remove extra whitespace
    return " ".join(result.split())

text_replacements = load_text_replacements()