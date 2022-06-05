import re

from utils.console import print_step, print_substep
import praw
import random
from dotenv import load_dotenv
from os import getenv, environ

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
    load_dotenv()
    reddit = praw.Reddit(client_id=getenv("REDDIT_CLIENT_ID"), client_secret=getenv("REDDIT_CLIENT_SECRET"),
                         user_agent="Accessing AskReddit threads", username=getenv("REDDIT_USERNAME"),
                         password=getenv("REDDIT_PASSWORD"), )
    """
    Ask user for subreddit input
    """
    if not getenv("SUBREDDIT"):
        subreddit = reddit.subreddit(
            input("What subreddit would you like to pull from? "))  # if the env isnt set, ask user
    else:
        print_substep(f"Using subreddit: r/{getenv('SUBREDDIT')} from environment variable config")
        subreddit = reddit.subreddit(
            getenv("SUBREDDIT"))  # Allows you to specify in .env. Done for automation purposes.

    if getenv('POST_ID'):
        submission = reddit.submission(id=getenv('POST_ID'))
    else:
        threads = subreddit.hot(limit=25)
        submission = list(threads)[random.randrange(0, 25)]
    submission = check_done(submission)
    if submission == None:
        return get_subreddit_threads()

    print_substep(
        f'subreddit thread is: {submission.title}\n(if you dont like this, you can change it by exiting and rerunning the program)')

    environ["VIDEO_TITLE"] = str(textify(submission.title))
    environ["VIDEO_ID"] = str(textify(submission.id))
    try:

        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["comments"] = []

        for top_level_comment in submission.comments:
            if len(top_level_comment.body) <= 250:
                content["comments"].append(
                    {"comment_body": top_level_comment.body, "comment_url": top_level_comment.permalink,
                    "comment_id": top_level_comment.id, })

    except AttributeError as e:
        pass
    print_substep("Received subreddit threads Successfully.", style="bold green")
    return content
