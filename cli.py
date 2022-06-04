import argparse

from main import main
from utils.console import print_substep


def program_options():
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
        "-S",
        "--subreddit",
        help="Use another sub-reddit.",
        action="store"
    )
    # this one accepts link as input, defaults to the minecraft video
    # does not accept file or already downloaded background yet.
    parser.add_argument(
        "-b",
        "--background",
        help="Use another video background for video (accepts link).",
        action="store"
    )

    args = parser.parse_args()

    try:
        if args.create:
            main(args.subreddit, args.background)
        else:
            print_substep("Error occured!", style="bold red")
            raise SystemExit()
    except (
        ConnectionError,
        KeyboardInterrupt,
    ):
        ...


program_options()
