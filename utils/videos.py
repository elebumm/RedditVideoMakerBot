import json
import os
import time
from os import getenv

from praw.models import Submission

from utils.console import print_step


def check_done(
    redditobj: dict[str],
) -> Submission:
    # don't set this to be run anyplace that isn't subreddit.py bc of inspect stack
    """Checks if the chosen post has already been generated

    Args:
        redditobj (dict[str]): Reddit object gotten from reddit/subreddit.py

    Returns:
        dict[str]|None: Reddit object in args
    """

    with open("./video_creation/data/videos.json", "r", encoding="utf-8") as done_vids_raw:
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


def save_data(filename: str, reddit_title: str, reddit_id: str):
    """Saves the videos that have already been generated to a JSON file in video_creation/data/videos.json

    Args:
        filename (str): The finished video title name
        @param filename:
        @param reddit_id:
        @param reddit_title:
    """
    with open("./video_creation/data/videos.json", "r+", encoding="utf-8") as raw_vids:
        done_vids = json.load(raw_vids)
        if reddit_id in [video["id"] for video in done_vids]:
            return  # video already done but was specified to continue anyway in the .env file
        payload = {
            "id": reddit_id,
            "time": str(int(time.time())),
            "background_credit": str(os.getenv("background_credit")),
            "reddit_title": reddit_title,
            "filename": filename,
        }
        done_vids.append(payload)
        raw_vids.seek(0)
        json.dump(done_vids, raw_vids, ensure_ascii=False, indent=4)
