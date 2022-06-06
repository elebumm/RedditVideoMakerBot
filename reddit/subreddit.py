import random
import os
import re

import praw
from prawcore.exceptions import (
    OAuthException,
    ResponseException,
    RequestException,
    BadRequest
)
from dotenv import load_dotenv
from rich.console import Console

from utils.console import print_step, print_substep


def get_subreddit_threads(subreddit_, thread_link_):
    """
    Takes subreddit_ as parameter which defaults to None, but in this
    case since it is None, it would raise ValueError, thus defaulting
    to AskReddit.

    Returns a list of threads from the AskReddit subreddit.
    """

    console = Console()

    global submission
    load_dotenv()

    if os.getenv("REDDIT_2FA", default="no").casefold() == "yes":
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n", end=" "
        )
        code = input("> ")
        pw = os.getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = os.getenv("REDDIT_PASSWORD")

    content = {}
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID").strip(),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET").strip(),
            user_agent="Accessing AskReddit threads",
            username=os.getenv("REDDIT_USERNAME").strip(),
            password=passkey.strip(),
        )
    except (
            OAuthException,
            ResponseException,
            RequestException,
            BadRequest
        ):
        console.print(
            "[bold red]There is something wrong with the .env file, kindly check:[/bold red]\n"
            + "1. ClientID\n"
            + "2. ClientSecret\n"
            + "3. If these variables are fine, kindly check other variables."
            + "4. Check if the type of Reddit app created is script (personal use script)."
        )


    # If the user specifies that he doesnt want a random thread, or if
    # he doesn't insert the "RANDOM_THREAD" variable at all, ask the thread link
    if thread_link_ is not None:
        thread_link = thread_link_
        print_step("Getting the inserted thread...")
        submission = reddit.submission(url=thread_link)
    else:
        try:
            if subreddit_ is None:
                raise ValueError

            subreddit = reddit.subreddit(subreddit_)
        except ValueError:
            if os.getenv("SUBREDDIT"):
                subreddit = reddit.subreddit(
                    re.sub(r"r\/", "", os.getenv("SUBREDDIT").strip())
                )
            else:
                subreddit = reddit.subreddit("askreddit")
                print_substep("Subreddit not defined. Using AskReddit.")

        threads = subreddit.hot(limit=25)
        submission = list(threads)[random.randrange(0, 25)]

    print_substep(f"Video will be: [cyan]{submission.title}[/cyan] :thumbsup:")

    try:
        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["thread_post"] = submission.selftext
        content["comments"] = []

        for top_level_comment in submission.comments:
            if not top_level_comment.stickied:
                content["comments"].append(
                    {
                        "comment_body": top_level_comment.body,
                        "comment_url": top_level_comment.permalink,
                        "comment_id": top_level_comment.id,
                    }
                )
    except AttributeError:
        pass

    print_substep("AskReddit threads retrieved successfully.", style="bold green")

    return content
