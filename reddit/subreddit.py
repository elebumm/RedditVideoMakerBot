import re

from utils.console import print_step, print_substep
import praw
import random
from dotenv import load_dotenv
import os


def ascifi(text):
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def get_subreddit_threads():
    """
    Returns a list of threads from the AskReddit subreddit.
    """

    print_step("Getting subreddit threads...")

    content = {}
    load_dotenv()
    reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"), client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                         user_agent="Accessing AskReddit threads", username=os.getenv("REDDIT_USERNAME"),
                         password=os.getenv("REDDIT_PASSWORD"), )
    """
    Ask user for subreddit input
    """
    if not os.getenv("SUBREDDIT"):
        subreddit = reddit.subreddit(
            input("What subreddit would you like to pull from? "))  # if the env isnt set, ask user
    else:
        print_substep(f"Using subreddit: r/{os.getenv('SUBREDDIT')} from environment variable config")
        subreddit = reddit.subreddit(
            os.getenv("SUBREDDIT"))  # Allows you to specify in .env. Done for automation purposes.

    threads = subreddit.hot(limit=25)
    submission = list(threads)[random.randrange(0, 25)]
    print_substep(f'subreddit thread is: {submission.title}\n(if you dont like this, you can change it by exiting and rerunning the program)')

    os.environ["VIDEO_TITLE"] = str(ascifi(submission.title))
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
    print_substep("Received subreddit threads Successfully.", style="bold green")
    return content
