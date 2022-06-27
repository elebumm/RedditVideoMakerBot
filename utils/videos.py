import json
from os import getenv

from utils.console import print_step


def check_done(
    redditobj: dict[str],
) -> dict[
    str
] | None:  # don't set this to be run anyplace that isn't subreddit.py bc of inspect stack
    """Checks if the chosen post has already been generated

    Args:
        redditobj (dict[str]): Reddit object gotten from reddit/subreddit.py

    Returns:
        dict[str]|None: Reddit object in args
    """

    with open("./video_creation/data/videos.json", "r") as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    for video in done_videos:
        if video["id"] == str(redditobj):
            if getenv("POST_ID"):
                print_step(
                    "You already have done this video but since it was declared specifically in the .env file the program will continue"
                )
                return redditobj
            print_step("Getting new post as the current one has already been done")
            return None
    return redditobj
