import argparse


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
    # this one accepts link as input, as well as already downloaded video,
    # defaults to the minecraft video.
    parser.add_argument(
        "-b",
        "--background",
        help="Use another video background for video (accepts link).",
        action="store"
    )
    parser.add_argument( # only accepts the name of subreddit, not links.
        "-S",
        "--subreddit",
        help="Use another sub-reddit.",
        action="store"
    )
    # show most of the background processes of the program
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show the processes of program.",
        action="store_true"
    )

    args = parser.parse_args()

    try:
        ...
    except (
        ConnectionError,
        KeyboardInterrupt
    ):
        ...


program_options()
