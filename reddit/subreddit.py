from utils.console import print_markdown, print_step, print_substep
from praw import Reddit
import random
from dotenv import load_dotenv
import os


def get_subreddit_threads():

    """
    Returns a list of threads from the AskReddit subreddit.
    """

    print_step("Getting AskReddit threads...")
    passkey = handle_2FA()
    reddit = Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing AskReddit threads",
        username=os.getenv("REDDIT_USERNAME"),
        password=passkey,
    )

    subreddit = choose_subreddit(reddit)

    threads = subreddit.hot(limit=25)
    submission = list(threads)[random.randrange(0, 25)]
    print_substep(f"Video will be: {submission.title} :thumbsup:")

    content = build_content_comments(submission)
   

            
    print_substep("Received AskReddit threads successfully.", style="bold green")

    return content

def handle_2FA():
    if os.getenv("REDDIT_2FA").lower() == "yes":
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n"
        )
        code = input("> ")
        print()
        pw = os.getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = os.getenv("REDDIT_PASSWORD")
        
    return passkey

def choose_subreddit(reddit):
    if os.getenv("SUBREDDIT"):
        subreddit = reddit.subreddit(os.getenv("SUBREDDIT"))
    else:
        # ! Prompt the user to enter a subreddit
        try:
            subreddit_name = input("What subreddit would you like to pull from? ")
            subreddit = reddit.subreddit(
                subreddit_name
            )
        except ValueError:
            subreddit = reddit.subreddit("AskReddit")
            print_substep("Subreddit not defined. Using AskReddit.")
    
    return subreddit

def build_content_comments(submission):
    try:
        content = { 'thread_url': submission.url, 'thread_title': submission.title }
        content["comments"] = []

        for top_level_comment in submission.comments:
            content["comments"].append(
                {
                    "comment_body": top_level_comment.body,
                    "comment_url": top_level_comment.permalink,
                    "comment_id": top_level_comment.id,
                }
            )

    except AttributeError as e:
        pass

    return content