from asyncio.windows_events import NULL
from utils.console import print_markdown, print_step, print_substep
from dotenv import load_dotenv
import os, random, praw, re

def get_random_submission(reddit , subreddit_name):
    subreddit = reddit.subreddit(re.sub(r"r\/", "", subreddit_name))
    threads = subreddit.hot(limit=25)
    return list(threads)[random.randrange(0, 25)]

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

    submission = NULL;

    try:
        if os.getenv("SUBMISSION_ID"):
            print_step("Getting submissions from " + os.getenv("SUBMISSION_ID") + " based on .env file value")
            submission = reddit.submission(os.getenv("SUBMISSION_ID"))
        elif os.getenv("SUBREDDIT"):
            print_step("Getting a radon submission from " + os.getenv("SUBREDDIT") + " based on .env file value")
            submission = get_random_submission(reddit , os.getenv("SUBREDDIT"))
        else:
            print_step("Choose your option : ")
            print_substep("1: Enter subreddit to pull randomly from")
            print_substep("2: Enter a submission to ID")
            print_substep("3: Pull randomly from AskReddit")
            option = int(input("Enter the option number : "))
            if option == 1:
                submission = get_random_submission(reddit , input("What subreddit would you like to pull from? "))
            elif option == 2:
                submission = reddit.submission(input("Enter submission ID : "));
            else:
                submission = get_random_submission(reddit , "askreddit")
    except ValueError:
         print_substep("Subreddit not defined. Using AskReddit.")
         submission = get_random_submission(reddit , "askreddit")
        
    print_substep(f"Video will be: {submission.title} :thumbsup:")
    try:

        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
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

    except AttributeError as e:
        pass
    print_substep("Received AskReddit threads successfully.", style="bold green")

    return content
