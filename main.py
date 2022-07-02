#!/usr/bin/env python

from subprocess import Popen
from os import getenv, name
from dotenv import load_dotenv
from reddit.subreddit import get_subreddit_threads
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step
from utils.checker import check_env

# from utils.checker import envUpdate
from video_creation.background import download_background, chop_background_video
from video_creation.final_video import make_final_video
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.voices import save_text_to_mp3

VERSION = "2.2.1"
print(
    """
██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║███████╗██████╔╝██████╔╝██║   ██║        ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝         ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
)
# Modified by JasonLovesDoggo
print_markdown(
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue. You can find solutions to many common problems in the [Documentation](https://luka-hietala.gitbook.io/documentation-for-the-reddit-bot/)"
)
print_step(f"You are using V{VERSION} of the bot")

def main(POST_ID=None):
    cleanup()
    reddit_object = get_subreddit_threads(POST_ID)
    length, number_of_comments = save_text_to_mp3(reddit_object)
    download_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    download_background()
    chop_background_video(length)
    make_final_video(number_of_comments, length, reddit_object)


def run_many(times):
    for x in range(1, times + 1):
        print_step(
            f'on the {x}{("st" if x == 1 else ("nd" if x == 2 else ("rd" if x == 3 else "th")))} iteration of {times}'
        )  # correct 1st 2nd 3rd 4th 5th....
        main()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


if __name__ == "__main__":
    if check_env() is not True:
        exit()
    load_dotenv()
    try:
        if getenv("TIMES_TO_RUN") and isinstance(int(getenv("TIMES_TO_RUN")), int):
            run_many(int(getenv("TIMES_TO_RUN")))

        elif len(getenv("POST_ID", "").split("+")) > 1:
            for index, post_id in enumerate(getenv("POST_ID", "").split("+")):
                index += 1
                print_step(
                    f'on the {index}{("st" if index == 1 else ("nd" if index == 2 else ("rd" if index == 3 else "th")))} post of {len(getenv("POST_ID", "").split("+"))}'
                )
                main(post_id)
                Popen("cls" if name == "nt" else "clear", shell=True).wait()
        else:
            main()
    except KeyboardInterrupt:
        print_markdown("## Clearing temp files")
        cleanup()
        exit()
