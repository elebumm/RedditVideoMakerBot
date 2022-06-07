import os
import shutil

from dotenv import load_dotenv
from rich.console import Console

from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video
from utils.console import print_markdown, print_substep
from setup_program import setup


def main(subreddit_=None, background=None, filename=None, thread_link_=None):
    """
    Load .env file if exists. If it doesnt exist, print a warning and
    launch the setup wizard. If there is a .env file, check if the
    required variables are set. If not, print a warning and launch the
    setup wizard.
    """

    console = Console()
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
        console.print(
            "[bold red] The .env file is invalid. Creating .env file.[/bold red]"
        )

    console.print("[bold]Checking environment variables...[/bold]")

    configured = True
    for val in REQUIRED_VALUES:
        if not os.getenv(val):
            print_substep(
                f"Please set the variable \"{val}\" in your .env file.", style="bold red"
            )
            configured = False

    try:
        float(os.getenv("OPACITY"))
    except (
            ValueError,
            FloatingPointError,
            TypeError,
        ):
        console.print(
            "[bold red]Please ensure that OPACITY is between 0 and 1 in .env file.[/bold red]"
        )
        raise SystemExit()

    if configured:
        console.print("[bold green]Enviroment Variables are set! Continuing...[/bold green]")

        reddit_object = get_subreddit_threads(subreddit_, thread_link_)
        length, number_of_comments = save_text_to_mp3(reddit_object)
        download_screenshots_of_reddit_posts(
            reddit_object,
            number_of_comments,
            os.getenv("THEME", "light")
        )
        download_background(background)
        chop_background_video(length)
        make_final_video(number_of_comments, filename)
    else:
        console.print(
            "[bold red]Looks like you need to set your Reddit credentials in the .env file. "
            + "Please follow the instructions in the README.md file to set them up.[/bold red]"
        )
        setup_ask = input("\033[1mLaunch setup wizard? [y/N] > \033[0m")
        if setup_ask in ["y", "Y"]:
            setup()
