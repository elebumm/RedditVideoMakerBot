import json
from os.path import exists

from utils import settings
from utils.console import print_substep
from utils.ai_methods import sort_by_similarity


def get_subreddit_undone(submissions: list, subreddit, times_checked=0, similarity_scores=None):
    """_summary_

    Args:
        submissions (list): List of posts that are going to potentially be generated into a video
        subreddit (praw.Reddit.SubredditHelper): Chosen subreddit

    Returns:
        Any: The submission that has not been done
    """
    # Second try of getting a valid Submission
    if times_checked and settings.config["ai"]["ai_similarity_enabled"]:
        print("Sorting based on similarity for a different date filter and thread limit..")
        submissions = sort_by_similarity(
            submissions, keywords=settings.config["ai"]["ai_similarity_enabled"]
        )

    # recursively checks if the top submission in the list was already done.
    if not exists("./video_creation/data/videos.json"):
        with open("./video_creation/data/videos.json", "w+") as f:
            json.dump([], f)
    with open("./video_creation/data/videos.json", "r", encoding="utf-8") as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    for i, submission in enumerate(submissions):
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
        if (
            submission.num_comments <= int(settings.config["reddit"]["thread"]["min_comments"])
            and not settings.config["settings"]["storymode"]
        ):
            print_substep(
                f'This post has under the specified minimum of comments ({settings.config["reddit"]["thread"]["min_comments"]}). Skipping...'
            )
            continue
        if settings.config["settings"]["storymode"]:
            if not submission.selftext:
                print_substep("You are trying to use story mode on post with no post text")
                continue
            else:
                # Check for the length of the post text
                if len(submission.selftext) > (
                    settings.config["settings"]["storymode_max_length"] or 2000
                ):
                    print_substep(
                        f"Post is too long ({len(submission.selftext)}), try with a different post. ({settings.config['settings']['storymode_max_length']} character limit)"
                    )
                    continue
                elif len(submission.selftext) < 30:
                    continue
        if settings.config["settings"]["storymode"] and not submission.is_self:
            continue
        if similarity_scores is not None:
            return submission, similarity_scores[i].item()
        return submission
    print("all submissions have been done going by top submission order")
    VALID_TIME_FILTERS = [
        "day",
        "hour",
        "month",
        "week",
        "year",
        "all",
    ]  # set doesn't have __getitem__
    index = times_checked + 1
    if index == len(VALID_TIME_FILTERS):
        print("All submissions have been done.")

    return get_subreddit_undone(
        subreddit.top(
            time_filter=VALID_TIME_FILTERS[index],
            limit=(50 if int(index) == 0 else index + 1 * 50),
        ),
        subreddit,
        times_checked=index,
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
