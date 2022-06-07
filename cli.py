import argparse

from main import main
from setup_program import setup
from utils.console import print_substep


def program_options():

    description = """\
    Create Reddit Videos with one command.
    """

    parser = argparse.ArgumentParser(
        prog="RedditVideoMakerBot", # can be renamed, just a base
        usage="RedditVideoMakerBot [OPTIONS]",
        description=description
    )
    parser.add_argument(
        "-c", "--create",
        help="Create a video (uses the defaults).",
        action="store_true"
    )
    parser.add_argument( # only accepts the name of subreddit, not links.
        "-s", "--subreddit",
        help="Specify a subreddit.",
        action="store"
    )
    parser.add_argument(
        "-b", "--background",
        help="Specify a video background for video (accepts link and file).",
        action="store"
    )
    parser.add_argument(
        "-f", "--filename",
        help="Specify a filename for the video.",
        action="store"
    )
    parser.add_argument(
        "-t", "--thread",
        help="Use the given thread link instead of random.",
        action="store"
    )
    parser.add_argument(
        "-n", "--number",
        help="Specify number of comments to include in the video.",
        action="store"
    )
    parser.add_argument(
        "--setup", "--setup",
        help="(Re)setup the program.",
        action="store_true"
    )

    args = parser.parse_args()

    try:
        if args.create:
            trial = 0
            while trial < 3:
                create = main(
                    args.subreddit,
                    args.background,
                    args.filename,
                    args.thread,
                    args.number,
                )
                if not create:
                    try_again = input("Something went wrong! Try again? [y/N] > ").strip()
                    if try_again in ["y", "Y"]:
                        trial += 1
                        continue

                break
        elif args.setup:
            setup()
        else:
            print_substep("Error occured!", style_="bold red")
            raise SystemExit()
    except KeyboardInterrupt:
        print_substep("\nOperation Aborted!", style_="bold red")


if __name__ == "__main__":
    program_options()
