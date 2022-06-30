from dotenv import load_dotenv
from prawcore.exceptions import (
    OAuthException,
    ResponseException,
    RequestException,
    BadRequest
)
import random
import os
import re
from os import getenv, environ

import praw

from utils.console import print_step, print_substep
from utils.subreddit import get_subreddit_undone
from utils.videos import check_done
from praw.models import MoreComments

TEXT_WHITELIST = set(
    "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890")


def textify(text):
    return "".join(filter(TEXT_WHITELIST.__contains__, text))


def try_env(param, backup):
    try:
        return environ[param]
    except KeyError:
        return backup


def get_subreddit_threads(subreddit_, thread_link_, number_of_comments):
    """
    Takes subreddit_ as parameter which defaults to None, but in this
    case since it is None, it would raise ValueError, thus defaulting
    to AskReddit.

    Returns a list of threads from the provided subreddit.
    """

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
        print_substep(
            "[bold red]There is something wrong with the .env file, kindly check:[/bold red]\n"
            + "1. ClientID\n"
            + "2. ClientSecret\n"
            + "3. If these variables are fine, kindly check other variables.\n"
            + "4. Check if the type of Reddit app created is script (personal use script)."
        )

    # If the user specifies that he doesnt want a random thread, or if
    # he doesn't insert the "RANDOM_THREAD" variable at all, ask the thread link
    while True:
        if thread_link_ is not None:
            thread_link = thread_link_
            print_step("Getting the inserted thread...")
            submission = reddit.submission(url=thread_link)
        else:
            try:
                if subreddit_ is None:
                    raise ValueError

                subreddit = reddit.subreddit(
                    re.sub(r"r\/", "", subreddit_.strip())
                )
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

        try:
            with open("created_videos", "r", encoding="utf-8") as reference:
                videos = list(reference.readlines())

            if submission.title in videos:
                print_substep(
                    "[bold]There is already a video for thread: [cyan]"
                    + f"{submission.title}[/cyan]. Finding another one.[/bold]"
                )
                continue
        except FileNotFoundError:
            break

        if len(submission.comments) == 0:
            print_substep(
                "The thread do not contain any comments. Searching for new one.", style_="bold"
            )

    upvotes = submission.score
    ratio = submission.upvote_ratio * 100
    num_comments = submission.num_comments

    print_substep(
        f"[bold]Video will be: [cyan]{submission.title}[/cyan] :thumbsup:\n"
        + f"[blue] Thread has {upvotes} and upvote ratio of {ratio}%\n"
        + f"And has a {num_comments}[/blue].\n"
    )

    try:
        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["thread_post"] = submission.selftext
        content["comments"] = []

        comment_count = 0
        for top_level_comment in submission.comments:
            if number_of_comments is not None:
                if comment_count == number_of_comments:
                    break

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

    print_substep("AskReddit threads retrieved successfully.",
                  style="bold green")

    content["thread_url"] = f"https://reddit.com{submission.permalink}"
    content["thread_title"] = submission.title
    content["thread_post"] = submission.selftext
    content["comments"] = []
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        if top_level_comment.body in ["[removed]", "[deleted]"]:
            continue  # # see https://github.com/JasonLovesDoggo/RedditVideoMakerBot/issues/78
        if not top_level_comment.stickied:
            if len(top_level_comment.body) <= int(try_env("MAX_COMMENT_LENGTH", 500)):
                content["comments"].append(
                    {
                        "comment_body": top_level_comment.body,
                        "comment_url": top_level_comment.permalink,
                        "comment_id": top_level_comment.id,
                    }
                )
    print_substep("Received subreddit threads Successfully.",
                  style="bold green")
    return content
