import re
import sys
from datetime import datetime
import time as pytime
from time import sleep

from requests import Response

if sys.version_info[0] >= 3:
    from datetime import timezone


def check_ratelimit(response: Response):
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


def sleep_until(time):
    """
    Pause your program until a specific end time.
    'time' is either a valid datetime object or unix timestamp in seconds (i.e. seconds since Unix epoch)
    """
    end = time

    # Convert datetime to unix timestamp and adjust for locality
    if isinstance(time, datetime):
        # If we're on Python 3 and the user specified a timezone, convert to UTC and get tje timestamp.
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

    profanity = [
        ["a word", r"(?:^|\W)ass(?:$|\W)", "arse", "asdf", "asdf", "asdf"],
        ["b word", "bastard", r"blow job", r"blowie", r"bitch", r"asdf"],
        ["c word", "cunt", r"(?:^|\W)cum(?:$|\W)", r"(?:^|\W)coon(?:$|\W)", r"cock", r"clit"],
        ["d word", "dick", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["e word", "asdf", r"asdf", r"asdf", r"asdf", r"asdf"],
        ["f word", r"fuck", "faggot", "fag", "asdf", "asdf"],
        ["g word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["h word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["i word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["j word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["k word", "knob", "kum", r"koon", r"asdf", r"asdf"],
        ["l word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["m word", "minge", r"(?:^|\W)mong(?:$|\W)", r"motherfucker", r"asdf", r"asdf"],
        ["n word", "nigga", "nigger", r"asdf", r"asdf", r"asdf"],
        ["o word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["p word", "pussy", "piss", "punani", "prick", "asdf"],
        ["q word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["r word", "retard", "retards", r"asdf", r"asdf", r"asdf"],
        ["s word", "slut", "shit", r"asdf", r"asdf", r"asdf"],
        ["t word", "twat", r"(?:^|\W)tit(?:$|\W)", r"(?:^|\W)tits(?:$|\W)", r"titties", r"asdf"],
        ["u word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["v word", "asdf", "asdf", r"asdf", r"asdf", r"asdf"],
        ["w word", "wanker", "asdf", "asdf", r"asdf", r"asdf"],
    ]

    result = re.sub(regex_urls, "url", text)

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%—“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", result)
    result = result.replace("+", "plus").replace("&", "and")
    #print(result)
    for x in range(0, len(profanity)):
        for y in range(1, len(profanity[0])):
            # print("row: " + str(x))
            # print("column: " + str(y))
            result = re.sub(profanity[x][y], profanity[x][0], result, flags=re.I)
            # print(regex[x][y])
    # remove extra whitespace
    print(result)
    return " ".join(result.split())
