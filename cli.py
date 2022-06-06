import argparse

from prawcore.exceptions import OAuthException
from rich.console import Console

from main import main
from setup_program import setup
from utils.console import print_substep


def program_options():
    console = Console()

    description = """\
        DESCRIPTION HERE.
    """

    parser = argparse.ArgumentParser(
        prog="RedditVideoMakerBot", # can be renamed, just a base
        usage="RedditVideoMakerBot [OPTIONS]",
        description=description
    )
    parser.add_argument(
        "-c",
        "--create",
        help="Create a video.",
        action="store_true"
    )
    parser.add_argument( # only accepts the name of subreddit, not links.
        "-s",
        "--subreddit",
        help="Use another sub-reddit.",
        action="store"
    )
    parser.add_argument(
        "-b",
        "--background",
        help="Use another video background for video (accepts link).",
        action="store"
    )
    parser.add_argument(
        "-f",
        "--filename",
        help="Set a filename for the video.",
        action="store"
    )
    parser.add_argument(
        "-t",
        "--thread",
        help="Use the given thread link instead of randomized.",
        action="store"
    )
    parser.add_argument(
        "--setup",
        "--setup",
        help="Setup the program.",
        action="store_true"
    )

    args = parser.parse_args()

    try:
        if args.create:
            main(
                args.subreddit,
                args.background,
                args.filename,
                args.thread,
            )
        elif args.setup:
            setup()
        else:
            print_substep("Error occured!", style="bold red")
            raise SystemExit()
    except (
        ConnectionError,
        KeyboardInterrupt,
    ):
        print_substep("Error occured!", style="bold red")
    except OAuthException:
        console.print(
            "There is something wrong with the .env file, kindly check:[/bold]\n"
            + "1. ClientID\n"
            + "2. ClientSecret\n"
            + "3. If these variables are fine, kindly check other variables."
        )


if __name__ == "__main__":
    program_options()
