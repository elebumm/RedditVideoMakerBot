import re
from os import getenv

import praw
from praw.models import MoreComments

from utils.console import print_step, print_substep
from utils.subreddit import get_subreddit_undone
from utils.videos import check_done


def get_subreddit_threads(POST_ID: str):
    """
    Returns a list of threads from the AskReddit subreddit.
    """

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
    username = getenv("REDDIT_USERNAME")
    if username.casefold().startswith("u/"):
        username = username[2:]
    reddit = praw.Reddit(
        client_id=getenv("REDDIT_CLIENT_ID"),
        client_secret=getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing Reddit threads",
        username=username,
        passkey=passkey,
        check_for_async=False,
    )

    # Ask user for subreddit input
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
        subreddit_choice = getenv("SUBREDDIT")
        if subreddit_choice.casefold().startswith("r/"):  # removes the r/ from the input
            subreddit_choice = subreddit_choice[2:]
        subreddit = reddit.subreddit(
            subreddit_choice
        )  # Allows you to specify in .env. Done for automation purposes.

    if POST_ID:  # would only be called if there are multiple queued posts
        submission = reddit.submission(id=POST_ID)
    elif getenv("POST_ID") and len(getenv("POST_ID").split("+")) == 1:
        submission = reddit.submission(id=getenv("POST_ID"))
    else:

        threads = subreddit.hot(limit=25)
        submission = get_subreddit_undone(threads, subreddit)
    submission = check_done(submission)  # double-checking
    if submission is None:
        return get_subreddit_threads(POST_ID)  # submission already done. rerun
    upvotes = submission.score
    ratio = submission.upvote_ratio * 100
    num_comments = submission.num_comments

    print_substep(f"Video will be: {submission.title} :thumbsup:", style="bold green")
    print_substep(f"Thread has {upvotes} upvotes", style="bold blue")
    print_substep(f"Thread has a upvote ratio of {ratio}%", style="bold blue")
    print_substep(f"Thread has {num_comments} comments", style="bold blue")

    content["thread_url"] = f"https://reddit.com{submission.permalink}"
    content["thread_title"] = submission.title
    content["thread_post"] = submission.selftext
    content["thread_id"] = submission.id
    content["comments"] = []

    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue
        if top_level_comment.body in ["[removed]", "[deleted]"]:
            continue  # # see https://github.com/JasonLovesDoggo/RedditVideoMakerBot/issues/78
        if not top_level_comment.stickied:
            if len(top_level_comment.body) <= int(getenv("MAX_COMMENT_LENGTH", "500")):
                if (
                    top_level_comment.author is not None
                ):  # if errors occur with this change to if not.
                    content["comments"].append(
                        {
                            "comment_body": top_level_comment.body,
                            "comment_url": top_level_comment.permalink,
                            "comment_id": top_level_comment.id,
                        }
                    )
    print_substep("Received subreddit threads Successfully.", style="bold green")
    return content
