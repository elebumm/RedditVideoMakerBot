from numpy import Infinity
from rich.console import Console
from utils.console import print_step, print_substep, print_markdown
from dotenv import load_dotenv
import os
import random
import praw
import re

console = Console()


def get_subreddit_threads():
    global submission
    """
    Returns a list of threads from the AskReddit subreddit.
    """

    load_dotenv()

    if os.getenv("REDDIT_2FA", default="no").casefold() == "yes":
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n"
        )
        code = input("> ")
        print()
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

    # If the user specifies that he doesnt want a random thread, or if he doesn't insert the "RANDOM_THREAD" variable at all, ask the thread link
    if not os.getenv("RANDOM_THREAD") or os.getenv("RANDOM_THREAD") == "no":
        print_substep("Insert the full thread link:", style="bold green")
        thread_link = input()
        print_step("Getting the inserted thread...")
        submission = reddit.submission(url=thread_link)
    else:
        # Otherwise, picks a random thread from the inserted subreddit
        if os.getenv("SUBREDDIT"):
            subreddit = reddit.subreddit(re.sub(r"r\/", "", os.getenv("SUBREDDIT")))
        else:
            # ! Prompt the user to enter a subreddit
            try:
                subreddit = reddit.subreddit(
                    re.sub(
                        r"r\/",
                        "",
                        input("What subreddit would you like to pull from? "),
                    )
                )
            except ValueError:
                subreddit = reddit.subreddit("askreddit")
                print_substep("Subreddit not defined. Using AskReddit.")

        threads = subreddit.hot(limit=25)
        submission = list(threads)[random.randrange(0, 25)]

    upvotes=submission.score
    ratio=submission.upvote_ratio * 100
    num_comments=submission.num_comments

    console.log(f"[bold green] Video will be: {submission.title} :thumbsup:")
    console.log(f"[bold blue] Thread has " + str(upvotes) + " upvotes")
    console.log(f"[bold blue] Thread has a upvote ratio of " + str(ratio) + "%")
    console.log(f"[bold blue] Thread has " + str(num_comments) + " comments")
    console.log("Getting video comments...")
    try:
        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["thread_post"] = submission.selftext
        content["comments"] = []

        for top_level_comment in submission.comments:
            COMMENT_LENGTH_RANGE = [0, Infinity]
            if os.getenv("COMMENT_LENGTH_RANGE"):
                COMMENT_LENGTH_RANGE = [int(i) for i in os.getenv("COMMENT_LENGTH_RANGE").split(",")]                
            if COMMENT_LENGTH_RANGE[0] <= len(top_level_comment.body) <= COMMENT_LENGTH_RANGE[1]:
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
    print_substep("Received AskReddit threads successfully.", style="bold green")

    return content
