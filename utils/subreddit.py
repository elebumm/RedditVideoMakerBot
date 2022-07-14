import json
from os.path import exists

from utils import settings
from utils.console import print_substep


def get_subreddit_undone(submissions: list, subreddit):
    """_summary_

    Args:
        submissions (list): List of posts that are going to potentially be generated into a video
        subreddit (praw.Reddit.SubredditHelper): Chosen subreddit

    Returns:
        Any: The submission that has not been done
    """
    # recursively checks if the top submission in the list was already done.
    if not exists("./video_creation/data/videos.json"):
        with open("./video_creation/data/videos.json", "w+") as f:
            json.dump([], f)
    with open("./video_creation/data/videos.json", "r", encoding="utf-8") as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    for submission in submissions:
        if already_done(done_videos, submission):
            continue
        if submission.over_18:
            try:
                if not settings.config["settings"]["allow_nsfw"]:
                    print_substep("NSFW Post Detected. Skipping...")
                    continue
            except AttributeError:
                print_substep("NSFW settings not defined. Skipping NSFW post...")
        if submission.stickied:
            print_substep("This post was pinned by moderators. Skipping...")
            continue
        if submission.num_comments <= int(settings.config["reddit"]["thread"]["min_comments"]):
            print_substep(
                f'This post has under the specified minimum of comments ({settings.config["reddit"]["thread"]["min_comments"]}). Skipping...'
            )
            continue
        return submission
    print("all submissions have been done going by top submission order")
    return get_subreddit_undone(
        subreddit.top(time_filter="hour"), subreddit
    )  # all the videos in hot have already been done


def already_done(done_videos: list, submission) -> bool:
    """Checks to see if the given submission is in the list of videos

    Args:
        done_videos (list): Finished videos
        submission (Any): The submission

    Returns:
        Boolean: Whether the video was found in the list
    """

    for video in done_videos:
        if video["id"] == str(submission):
            return True
    return False
