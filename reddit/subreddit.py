import random
import os
import re

import praw
from dotenv import load_dotenv

from utils.console import print_step, print_substep


def get_subreddit_threads(subreddit_):
    """
    Takes subreddit_ as parameter which defaults to None, but in this
    case since it is None, it would raise ValueError, thus defaulting
    to AskReddit.

    Returns a list of threads from the AskReddit subreddit.
    """

    load_dotenv()

    print_step("Getting AskReddit threads...")

    if os.getenv("REDDIT_2FA", default="no").casefold() == "yes":
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n"
        )
        code = input("> ")
        pw = os.getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = os.getenv("REDDIT_PASSWORD")

    content = {}
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing AskReddit threads",
        username=os.getenv("REDDIT_USERNAME"),
        password=passkey,
    )

    try:
        if subreddit_ is None:
            raise ValueError

        subreddit = reddit.subreddit(subreddit_)
    except ValueError:
        if os.getenv("SUBREDDIT"):
            subreddit = reddit.subreddit(re.sub(r"r\/", "", os.getenv("SUBREDDIT")))
        else:
            subreddit = reddit.subreddit("askreddit")

        print_substep("Subreddit not defined. Using AskReddit.")

    threads = subreddit.hot(limit=25)
    submission = list(threads)[random.randrange(0, 25)]
    print_substep(f"Video will be: {submission.title} :thumbsup:")

    try:
        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["comments"] = []

        for top_level_comment in submission.comments:
            content["comments"].append(
                {
                    "comment_body": top_level_comment.body,
                    "comment_url": top_level_comment.permalink,
                    "comment_id": top_level_comment.id,
                }
            )
    except AttributeError as e:
        pass

    print_substep("AskReddit threads retrieved successfully.", style="bold green")

    return content
