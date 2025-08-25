import math
import re
import sys
from os import name
from pathlib import Path
from subprocess import Popen
from typing import NoReturn

import praw
from prawcore.exceptions import ResponseException

from reddit.subreddit import get_subreddit_threads
from utils import settings
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step, print_substep
from utils.ffmpeg_install import ffmpeg_install
from utils.version import checkversion
from video_creation.background import download_background_audio, download_background_video
from video_creation.final_video import make_final_video
from video_creation.screenshot_downloader import get_screenshots_of_reddit_posts
from video_creation.voices import save_text_to_mp3
from video_creation.background import chop_background, get_background_config

__VERSION__ = "3.3.0"

print_markdown(
    """# Reddit Video Maker Bot

██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ 
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗
██║ ██╔╝██╔════╝██╔══██╗██████╔╝█████╗  ██║  ██║██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║
█████╔╝ █████╗  ██████╔╝██████╔╝██╔══╝  ██║  ██║██║   ██║██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║
██╔═██╗ ██╔══╝  ██╔══██╗██╔═██╗ ██╔══╝  ██║  ██║╚██╗ ██╔╝██║██║  ██║███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║
██║  ██╗███████╗██║  ██║██║  ██╗███████╗██║  ██║ ╚████╔╝ ██║██████╔╝╚══════╝ ╚═════╝     ██║     ██║╚═╝  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ╚═══╝ ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"""
)
print_markdown(
    "### Thanks for using this tool! Feel free to contribute to this project on GitHub! If you have any questions, feel free to join my Discord server or submit a GitHub issue. You can find solutions to many common problems in the documentation: https://reddit-video-maker-bot.netlify.app/"
)
checkversion(__VERSION__)


def extract_post_id_from_url(url: str) -> str:
    """
    Extract the post ID from a Reddit URL.
    
    Args:
        url (str): Reddit post URL
        
    Returns:
        str: Post ID
    """
    # Handle different Reddit URL formats
    patterns = [
        r'reddit\.com/r/\w+/comments/(\w+)/',  # Standard format
        r'reddit\.com/comments/(\w+)/',        # Short format
        r'reddit\.com/r/\w+/comments/(\w+)',   # Without trailing slash
        r'reddit\.com/comments/(\w+)',         # Short format without trailing slash
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("Invalid Reddit URL format. Please provide a valid Reddit post URL.")


def get_post_from_url(url: str) -> dict:
    """
    Get Reddit post data from a specific URL.
    
    Args:
        url (str): Reddit post URL
        
    Returns:
        dict: Reddit post data
    """
    print_substep("Extracting post ID from URL...")
    
    try:
        post_id = extract_post_id_from_url(url)
        print_substep(f"Post ID extracted: {post_id}")
    except ValueError as e:
        print_substep(f"Error: {e}", style="red")
        sys.exit(1)
    
    print_substep("Logging into Reddit...")
    
    # Setup Reddit authentication
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
    
    try:
        reddit = praw.Reddit(
            client_id=settings.config["reddit"]["creds"]["client_id"],
            client_secret=settings.config["reddit"]["creds"]["client_secret"],
            user_agent="Accessing Reddit threads",
            username=username,
            passkey=passkey,
            check_for_async=False,
        )
    except ResponseException as e:
        if e.response.status_code == 401:
            print("Invalid credentials - please check them in config.toml")
            sys.exit(1)
    except Exception as e:
        print(f"Something went wrong: {e}")
        sys.exit(1)
    
    print_substep("Fetching post data...")
    
    try:
        submission = reddit.submission(id=post_id)
        # Force the submission to load all data
        submission.title
        submission.selftext
        submission.score
        submission.upvote_ratio
        submission.num_comments
        submission.permalink
        submission.over_18
        submission.is_self
    except Exception as e:
        print_substep(f"Error fetching post: {e}", style="red")
        sys.exit(1)
    
    # Check if post is NSFW
    if submission.over_18 and not settings.config["settings"]["allow_nsfw"]:
        print_substep("This post is NSFW and NSFW content is not allowed in your config.", style="red")
        sys.exit(1)
    
    # Check if post has content for story mode
    if settings.config["settings"]["storymode"]:
        if not submission.selftext:
            print_substep("This post has no text content for story mode.", style="red")
            sys.exit(1)
        
        if len(submission.selftext) > settings.config["settings"]["storymode_max_length"]:
            print_substep(f"Post is too long ({len(submission.selftext)} characters). Max allowed: {settings.config['settings']['storymode_max_length']}", style="red")
            sys.exit(1)
        
        if len(submission.selftext) < 30:
            print_substep("Post is too short (less than 30 characters).", style="red")
            sys.exit(1)
    
    # Build content dictionary
    content = {
        "thread_url": f"https://new.reddit.com{submission.permalink}",
        "thread_title": submission.title,
        "thread_id": submission.id,
        "is_nsfw": submission.over_18,
        "comments": []
    }
    
    # Process content based on story mode
    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 1:
            from utils.posttextparser import posttextparser
            content["thread_post"] = posttextparser(submission.selftext)
        else:
            content["thread_post"] = submission.selftext
    else:
        # Process comments (not used in story mode)
        for top_level_comment in submission.comments:
            if hasattr(top_level_comment, 'body') and top_level_comment.body not in ["[removed]", "[deleted]"]:
                if not top_level_comment.stickied:
                    from utils.voice import sanitize_text
                    sanitised = sanitize_text(top_level_comment.body)
                    if sanitised and sanitised != " ":
                        if len(top_level_comment.body) <= int(settings.config["reddit"]["thread"]["max_comment_length"]):
                            if len(top_level_comment.body) >= int(settings.config["reddit"]["thread"]["min_comment_length"]):
                                if top_level_comment.author is not None:
                                    content["comments"].append({
                                        "comment_body": top_level_comment.body,
                                        "comment_url": top_level_comment.permalink,
                                        "comment_id": top_level_comment.id,
                                    })
    
    # Display post information
    print_substep(f"Video will be: {submission.title} 👍", style="bold green")
    print_substep(f"Thread url is: {content['thread_url']} 👍", style="bold green")
    print_substep(f"Thread has {submission.score} upvotes", style="bold blue")
    print_substep(f"Thread has a upvote ratio of {submission.upvote_ratio * 100}%", style="bold blue")
    print_substep(f"Thread has {submission.num_comments} comments", style="bold blue")
    
    if settings.config["settings"]["storymode"]:
        print_substep(f"Post content length: {len(submission.selftext)} characters", style="bold blue")
    
    print_substep("Post data fetched successfully.", style="bold green")
    return content


def main() -> None:
    """Main function to process a specific Reddit post URL."""
    global redditid, reddit_object
    
    print_step("Reddit Video Maker Bot - Target Mode")
    print_substep("This mode allows you to create a video from a specific Reddit post URL.")
    
    # Get URL from user
    while True:
        url = input("\nEnter the Reddit post URL: ").strip()
        if url:
            break
        print_substep("Please enter a valid URL.", style="red")
    
    # Get post data
    reddit_object = get_post_from_url(url)
    redditid = id(reddit_object)
    
    # Process the post
    length, number_of_comments = save_text_to_mp3(reddit_object)
    length = math.ceil(length)
    
    get_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    
    bg_config = {
        "video": get_background_config("video"),
        "audio": get_background_config("audio"),
    }
    
    download_background_video(bg_config["video"])
    download_background_audio(bg_config["audio"])
    chop_background(bg_config, length, reddit_object)
    make_final_video(number_of_comments, length, reddit_object, bg_config)


def shutdown() -> NoReturn:
    """Cleanup and exit."""
    if "redditid" in globals():
        print_markdown("## Clearing temp files")
        cleanup(redditid)

    print("Exiting...")
    sys.exit()


if __name__ == "__main__":
    if sys.version_info.major != 3 or sys.version_info.minor not in [10, 11, 12, 13]:
        print(
            "Hey! Congratulations, you've made it so far (which is pretty rare with no Python 3.10). Unfortunately, this program only works on Python 3.10+. Please install Python 3.10+ and try again."
        )
        sys.exit()
    
    ffmpeg_install()
    directory = Path().absolute()
    config = settings.check_toml(
        f"{directory}/utils/.config.template.toml", f"{directory}/config.toml"
    )
    config is False and sys.exit()

    if (
        not settings.config["settings"]["tts"]["tiktok_sessionid"]
        or settings.config["settings"]["tts"]["tiktok_sessionid"] == ""
    ) and config["settings"]["tts"]["voice_choice"] == "tiktok":
        print_substep(
            "TikTok voice requires a sessionid! Check our documentation on how to obtain one.",
            "bold red",
        )
        sys.exit()
    
    try:
        main()
    except KeyboardInterrupt:
        shutdown()
    except ResponseException:
        print_markdown("## Invalid credentials")
        print_markdown("Please check your credentials in the config.toml file")
        shutdown()
    except Exception as err:
        config["settings"]["tts"]["tiktok_sessionid"] = "REDACTED"
        config["settings"]["tts"]["elevenlabs_api_key"] = "REDACTED"
        print_step(
            f"Sorry, something went wrong with this version! Try again, and feel free to report this issue at GitHub or the Discord community.\n"
            f"Version: {__VERSION__} \n"
            f"Error: {err} \n"
            f'Config: {config["settings"]}'
        )
        raise err
