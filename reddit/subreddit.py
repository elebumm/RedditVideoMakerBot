import re

from utils import settings
import praw
from praw.models import MoreComments

from utils.console import print_step, print_substep
from utils.subreddit import get_subreddit_undone
from utils.videos import check_done
from utils.voice import sanitize_text


def get_subreddit_threads(POST_ID: str):
    """
    Returns a list of threads from the AskReddit subreddit.
    """

    print_substep("Logging into Reddit.")

    content = {}
    if settings.config["reddit"]["creds"]["2fa"]:
        print("\nEnter your two-factor authentication code from your authenticator app.\n")
        code = input("> ")
        print()
        pw = settings.config["reddit"]["creds"]["password"]
        passkey = f"{pw}:{code}"
    else:
        passkey = settings.config["reddit"]["creds"]["password"]
    username = settings.config["reddit"]["creds"]["username"]
    if str(username).casefold().startswith("u/"):
        username = username[2:]
    reddit = praw.Reddit(
        client_id=settings.config["reddit"]["creds"]["client_id"],
        client_secret=settings.config["reddit"]["creds"]["client_secret"],
        user_agent="Accessing Reddit threads",
        username=username,
        passkey=passkey,
        check_for_async=False,
    )

    # Ask user for subreddit input
    print_step("Getting subreddit threads...")
    if not settings.config["reddit"]["thread"][
        "subreddit"
    ]:  # note to user. you can have multiple subreddits via reddit.subreddit("redditdev+learnpython")
        try:
            subreddit = reddit.subreddit(
                re.sub(r"r\/", "", input("What subreddit would you like to pull from? "))
                # removes the r/ from the input
            )
        except ValueError:
            subreddit = reddit.subreddit("askreddit")
            print_substep("Subreddit not defined. Using AskReddit.")
    else:
        sub = settings.config["reddit"]["thread"]["subreddit"]
        print_substep(f"Using subreddit: r/{sub} from TOML config")
        subreddit_choice = sub
        if str(subreddit_choice).casefold().startswith("r/"):  # removes the r/ from the input
            subreddit_choice = subreddit_choice[2:]
        subreddit = reddit.subreddit(
            subreddit_choice
        )  # Allows you to specify in .env. Done for automation purposes.

    if POST_ID:  # would only be called if there are multiple queued posts
        submission = reddit.submission(id=POST_ID)
    elif (
        settings.config["reddit"]["thread"]["post_id"]
        and len(str(settings.config["reddit"]["thread"]["post_id"]).split("+")) == 1
    ):
        submission = reddit.submission(id=settings.config["reddit"]["thread"]["post_id"])
    else:
        threads = subreddit.hot(limit=25)
        submission = get_subreddit_undone(threads, subreddit)
    submission = check_done(submission)  # double-checking
    if submission is None or not submission.num_comments:
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
            sanitised = sanitize_text(top_level_comment.body)
            if not sanitised or sanitised == " ":
                continue
            if len(top_level_comment.body) <= int(
                settings.config["reddit"]["thread"]["max_comment_length"]
            ):
                if (
                    top_level_comment.author is not None
                    and sanitize_text(top_level_comment.body) is not None
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
