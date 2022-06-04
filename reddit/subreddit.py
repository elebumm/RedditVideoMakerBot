import random
from os import getenv, environ

import praw

from utils.console import print_step, print_substep
from utils.videos import check_done

TEXT_WHITELIST = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890')


def textify(text):
    return ''.join(filter(TEXT_WHITELIST.__contains__, text))


def get_subreddit_threads():
    """
    Returns a list of threads from the AskReddit subreddit.
    """

    print_step("Getting subreddit threads...")
    content = {}
    if getenv("REDDIT_2FA").casefold() == "yes":
        print("\nEnter your two-factor authentication code from your authenticator app.\n")
        code = input("> ")
        print()
        pw = getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = getenv("REDDIT_PASSWORD")
    reddit = praw.Reddit(client_id=getenv("REDDIT_CLIENT_ID"), client_secret=getenv("REDDIT_CLIENT_SECRET"),
                         user_agent="Accessing AskReddit threads", username=getenv("REDDIT_USERNAME"),
                         passkey=passkey, )
    """
    Ask user for subreddit input
    """

    if getenv('POST_ID'):
        submission = reddit.submission(id=getenv('POST_ID'))
    else:
        if getenv("SUBREDDIT"):  # Allows you to specify in .env. Done for automation purposes.
            subreddit = reddit.subreddit(getenv("SUBREDDIT"))
        else:
            # Prompt the user to enter a subreddit
            try:
                subreddit = reddit.subreddit(input("What subreddit would you like to pull from? "))
            except ValueError:
                subreddit = reddit.subreddit("askreddit")
                print_substep("Subreddit not defined. Using AskReddit.")
        threads = subreddit.hot(limit=25)
        submission = list(threads)[random.randrange(0, 25)]
    submission = check_done(submission)
    print_substep(f"Video will be: {submission.title} :thumbsup:")

    environ["VIDEO_TITLE"] = str(textify(submission.title))  # todo use global instend of env vars
    environ["VIDEO_ID"] = str(textify(submission.id))
    try:

        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["comments"] = []

        for top_level_comment in submission.comments:
            content["comments"].append(
                {"comment_body": top_level_comment.body, "comment_url": top_level_comment.permalink,
                 "comment_id": top_level_comment.id, })

    except AttributeError as e:
        pass
    print_substep("Received subreddit thread Successfully.", style="bold green")
    return content
