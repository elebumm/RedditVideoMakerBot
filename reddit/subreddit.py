import re
from os import getenv, environ

import praw

from utils.console import print_step, print_substep
from utils.subreddit import get_subreddit_undone
from utils.videos import check_done
from praw.models import MoreComments

TEXT_WHITELIST = set("abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890")


def textify(text):
    return "".join(filter(TEXT_WHITELIST.__contains__, text))


def try_env(param, backup):
    try:
        return environ[param]
    except KeyError:
        return backup


def get_subreddit_threads():
    """
    Returns a list of threads from the AskReddit subreddit.
    """
    global submission
    print_substep("Logging into Reddit.")

    content = {}
    if str(getenv("REDDIT_2FA")).casefold() == "yes":
        print("\nEnter your two-factor authentication code from your authenticator app.\n")
        code = input("> ")
        print()
        pw = getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = getenv("REDDIT_PASSWORD")
    reddit = praw.Reddit(
        client_id=getenv("REDDIT_CLIENT_ID"),
        client_secret=getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing Reddit threads",
        username=getenv("REDDIT_USERNAME"),
        passkey=passkey,
        check_for_async=False,
    )
    """
	Ask user for subreddit input
	"""
    print_step("Getting subreddit threads...")
    if not getenv(
        "SUBREDDIT"
    ):  # note to user. you can have multiple subreddits via reddit.subreddit("redditdev+learnpython")
        try:
            subreddit = reddit.subreddit(
                re.sub(r"r\/", "", input("What subreddit would you like to pull from? "))
                # removes the r/ from the input
            )
        except ValueError:
            subreddit = reddit.subreddit("askreddit")
            print_substep("Subreddit not defined. Using AskReddit.")
    else:
        print_substep(f"Using subreddit: r/{getenv('SUBREDDIT')} from environment variable config")
        subreddit = reddit.subreddit(
            getenv("SUBREDDIT")
        )  # Allows you to specify in .env. Done for automation purposes.

    if getenv("POST_ID"):
        submission = reddit.submission(id=getenv("POST_ID"))
    else:
        threads = subreddit.hot(limit=25)
        submission = get_subreddit_undone(threads, subreddit)
    submission = check_done(submission)  # double checking
    if submission is None:
        return get_subreddit_threads()  # submission already done. rerun
    upvotes = submission.score
    ratio = submission.upvote_ratio * 100
    num_comments = submission.num_comments

    print_substep(f"Video will be: {submission.title} :thumbsup:", style="bold green")
    print_substep(f"Thread has {upvotes} upvotes", style="bold blue")
    print_substep(f"Thread has a upvote ratio of {ratio}%", style="bold blue")
    print_substep(f"Thread has {num_comments} comments", style="bold blue")
    environ["VIDEO_TITLE"] = str(textify(submission.title))  # todo use global instend of env vars
    environ["VIDEO_ID"] = str(textify(submission.id))

    content["thread_url"] = f"https://reddit.com{submission.permalink}"
    content["thread_title"] = submission.title
    # content["thread_content"] = submission.content
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
    print_substep("Received subreddit threads Successfully.", style="bold green")
    return content
