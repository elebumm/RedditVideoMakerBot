from typing import List
import json
from os import getenv
from utils.console import print_substep


def get_subreddit_undone(submissions: List, subreddit):
    """
    recursively checks if the top submission in the list was already done.
    """
    with open("./video_creation/data/videos.json", "r") as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    for submission in submissions:
        if already_done(done_videos, submission):
            continue
        if submission.over_18:
            try:
                if getenv("ALLOW_NSFW").casefold() == "false":
                    print_substep("NSFW Post Detected. Skipping...")
                    continue
            except AttributeError:
                print_substep("NSFW settings not defined. Skipping NSFW post...")
        return submission
    print("all submissions have been done going by top submission order")
    return get_subreddit_undone(
        subreddit.top(time_filter="hour"), subreddit
    )  # all of the videos in hot have already been done


def already_done(done_videos: list, submission):

    for video in done_videos:
        if video["id"] == str(submission):
            return True
    return False
