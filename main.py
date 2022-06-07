import os
import shutil

from dotenv import load_dotenv

import reddit.subreddit
from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video
from utils.console import print_markdown, print_substep
from setup_program import setup


def main(
        subreddit_=None,
        background=None,
        filename=None,
        thread_link_=None,
        number_of_comments=None
    ):
    """
    Load .env file if exists. If it doesnt exist, print a warning and
    launch the setup wizard. If there is a .env file, check if the
    required variables are set. If not, print a warning and launch the
    setup wizard.
    """
    load_dotenv()

    REQUIRED_VALUES = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME",
        "REDDIT_PASSWORD",
        "OPACITY"
    ]

    print_markdown(
        "### Thanks for using this tool! [Feel free to contribute to this project on "
        + "GitHub!](https://lewismenelaws.com) If you have any questions, feel free to"
        + " reach out to me on Twitter or submit a GitHub issue."
    )

    if not os.path.exists(".env"):
        shutil.copy(".env.template", ".env")
        print_substep("The .env file is invalid. Creating .env file.", style_="bold red")

    print_substep("Checking environment variables ...", style_="bold")

    configured = True
    for val in REQUIRED_VALUES:
        if not os.getenv(val):
            print_substep(
                f"Please set the variable \"{val}\" in your .env file.", style_="bold red"
            )
            configured = False

    if configured:
        print_substep("Enviroment Variables are set! Continuing ...", style_="bold green")

        reddit_object = get_subreddit_threads(
            subreddit_,
            thread_link_,
            number_of_comments
        )
        length, number_of_comments = save_text_to_mp3(reddit_object)
        download_screenshots_of_reddit_posts(
            reddit_object,
            number_of_comments,
            os.getenv("THEME", "light")
        )
        download_background(background)
        chop_background_video(length)
        make_final_video(number_of_comments, filename)

        with open("created_videos", "a", encoding="utf-8") as video_lists:
            video_lists.write(reddit.subreddit.submission.title)

        return True

    print_substep(
        "Looks like you need to set your Reddit credentials in the .env file. Please follow "
        + "the instructions in the README.md file to set them up.", style_="bold red"
    )
    if input("\033[1mLaunch setup wizard? [y/N] > \033[0m").strip() in ["y", "Y"]:
        setup()

    return False
