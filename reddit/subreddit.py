from re import sub
from praw import Reddit
from praw.models import MoreComments
from prawcore.exceptions import ResponseException

from utils import settings
from utils.ai_methods import sort_by_similarity
from utils.console import print_step, print_substep
from utils.posttextparser import posttextparser
from utils.subreddit import get_subreddit_undone
from utils.videos import check_done
from utils.voice import sanitize_text


def get_reddit_instance():
    """Initialize and return a Reddit instance."""
    print_substep("Logging into Reddit.")
    if settings.config["reddit"]["creds"]["2fa"]:
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n"
        )
        code = input("> ")
        print()
        password = settings.config["reddit"]["creds"]["password"]
        passkey = f"{password}:{code}"
    else:
        passkey = settings.config["reddit"]["creds"]["password"]

    username = settings.config["reddit"]["creds"]["username"]
    if str(username).casefold().startswith("u/"):
        username = username[2:]

    try:
        return Reddit(
            client_id=settings.config["reddit"]["creds"]["client_id"],
            client_secret=settings.config["reddit"]["creds"]["client_secret"],
            user_agent="Accessing Reddit threads",
            username=username,
            password=passkey,
            check_for_async=False,
        )
    except ResponseException as e:
        if e.response.status_code == 401:
            print("Invalid credentials - please check them in config.toml")
    except Exception:
        print("Something went wrong...")


def get_subreddit(reddit):
    """Get the subreddit based on user input or config."""
    if not settings.config["reddit"]["thread"]["subreddit"]:
        try:
            subreddit_name = sub(
                r"r\/", "", input("What subreddit would you like to pull from? ")
            )
            return reddit.subreddit(subreddit_name)
        except ValueError:
            print_substep("Subreddit not defined. Using AskReddit.")
            return reddit.subreddit("askreddit")
    else:
        subreddit_name = settings.config["reddit"]["thread"]["subreddit"]
        print_substep(f"Using subreddit: r/{subreddit_name} from TOML config")
        if str(subreddit_name).casefold().startswith("r/"):
            subreddit_name = subreddit_name[2:]
        return reddit.subreddit(subreddit_name)


def get_submission(reddit, subreddit, post_id):
    """Retrieve a submission based on post ID or subreddit."""
    if post_id:
        return reddit.submission(id=post_id)

    if (
        settings.config["reddit"]["thread"]["post_id"]
        and len(str(settings.config["reddit"]["thread"]["post_id"]).split("+")) == 1
    ):
        return reddit.submission(id=settings.config["reddit"]["thread"]["post_id"])

    if settings.config["ai"]["ai_similarity_enabled"]:
        threads = subreddit.hot(limit=50)
        keywords = [
            keyword.strip()
            for keyword in settings.config["ai"]["ai_similarity_keywords"].split(",")
        ]
        print(
            f"Sorting threads by similarity to the given keywords: {', '.join(keywords)}"
        )
        threads, similarity_scores = sort_by_similarity(threads, keywords)
        return get_subreddit_undone(
            threads, subreddit, similarity_scores=similarity_scores
        )

    threads = subreddit.hot(limit=25)
    return get_subreddit_undone(threads, subreddit)


def collect_comments(submission):
    """Collect comments from a submission."""
    comments = []
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, MoreComments):
            continue

        if top_level_comment.body in ["[removed]", "[deleted]"]:
            continue

        if not top_level_comment.stickied:
            sanitized_text = sanitize_text(top_level_comment.body)
            if sanitized_text and len(top_level_comment.body) <= int(
                settings.config["reddit"]["thread"]["max_comment_length"]
            ):
                if len(top_level_comment.body) >= int(
                    settings.config["reddit"]["thread"]["min_comment_length"]
                ):
                    if top_level_comment.author is not None:
                        comments.append(
                            {
                                "comment_body": top_level_comment.body,
                                "comment_url": top_level_comment.permalink,
                                "comment_id": top_level_comment.id,
                            }
                        )
    return comments


def get_subreddit_threads(post_id):
    """Main function to get subreddit threads."""
    reddit = get_reddit_instance()
    if not reddit:
        return

    print_step("Getting subreddit threads...")
    subreddit = get_subreddit(reddit)
    submission = get_submission(reddit, subreddit, post_id)

    if submission is None:
        return get_subreddit_threads(post_id)

    if (
        not submission.num_comments
        and settings.config["settings"]["storymode"] == "false"
    ):
        print_substep("No comments found. Skipping.")
        exit()

    submission = check_done(submission)

    content = {
        "thread_url": f"https://new.reddit.com/{submission.permalink}",
        "thread_title": submission.title,
        "thread_id": submission.id,
        "is_nsfw": submission.over_18,
        "comments": [],
    }

    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 1:
            content["thread_post"] = posttextparser(submission.selftext)
        else:
            content["thread_post"] = submission.selftext
    else:
        content["comments"] = collect_comments(submission)

    print_substep("Received subreddit threads Successfully.", style="bold green")
    return content
