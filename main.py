#!/usr/bin/env python
import math
import os
import re
from subprocess import Popen
from os import name
from sys import platform

from prawcore import ResponseException

from reddit.subreddit import get_subreddit_threads
from utils import settings
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step
from utils.id import id
from utils.version import checkversion
from video_creation.background import (
    download_background,
    chop_background_video,
    get_background_config,
)
from video_creation.final_video import make_final_video
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.voices import save_text_to_mp3

__VERSION__ = "2.4.2"

### 3 util functions. by github.com/notcooler ###
def getPlatform():
    plt = "unknown"
    if platform == "linux" or platform == "linux2":
        plt = "lin"
    elif platform == "win32":
        plt = "win"
    elif platform == "darwin":
        plt = "mac"
    return plt

def clear():
    if getPlatform() == "win":
        os.system('cls')
    elif getPlatform() == "lin" or getPlatform() == "mac":
        os.system('clear')
    else:
        pass
def setConsoleSize(*_x, **_y):
    x = '23'
    y = '78'
    if _x != None and len(_x) != 0: x = str(_x[0])
    if _y != None and len(_x) != 0: y = str(_x[1])
    if getPlatform() == "win":
        os.system(f'mode {y},{x}')
    elif getPlatform() == "lin" or getPlatform() == "mac":
        os.system(f'resize -s {x} {y}')
    else:
        pass

### end util functions ###

# Clear console #
clear()

# Set console size so the banner looks good. #
setConsoleSize(389, 20);

# Print Banner
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
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue. You can find solutions to many common problems in the [Documentation](): https://reddit-video-maker-bot.netlify.app/"
)
checkversion(__VERSION__)


def main(POST_ID=None):
    reddit_object = get_subreddit_threads(POST_ID)
    global redditid
    redditid = id(reddit_object)
    length, number_of_comments = save_text_to_mp3(reddit_object)
    length = math.ceil(length)
    download_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    bg_config = get_background_config()
    download_background(bg_config)
    chop_background_video(bg_config, length, reddit_object)
    make_final_video(number_of_comments, length, reddit_object, bg_config)


def run_many(times):
    for x in range(1, times + 1):
        print_step(
            f'on the {x}{("th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th")[x % 10]} iteration of {times}'
        )  # correct 1st 2nd 3rd 4th 5th....
        main()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


def shutdown():
    print_markdown("## Clearing temp files")
    try:
        redditid
    except NameError:
        print("Exiting...")
        exit()
    else:
        cleanup(redditid)
        print("Exiting...")
        exit()


if __name__ == "__main__":
    assert sys.version_info >= (3, 9), "Python 3.10 or higher is required"
    config = settings.check_toml("utils/.config.template.toml", "config.toml")
    config is False and exit()
    try:
        if len(config["reddit"]["thread"]["post_id"].split("+")) > 1:
            for index, post_id in enumerate(config["reddit"]["thread"]["post_id"].split("+")):
                index += 1
                print_step(
                    f'on the {index}{("st" if index % 10 == 1 else ("nd" if index % 10 == 2 else ("rd" if index % 10 == 3 else "th")))} post of {len(config["reddit"]["thread"]["post_id"].split("+"))}'
                )
                main(post_id)
                Popen("cls" if name == "nt" else "clear", shell=True).wait()
        elif config["settings"]["times_to_run"]:
            run_many(config["settings"]["times_to_run"])
        else:
            main()
    except KeyboardInterrupt:
        shutdown()
    except ResponseException:
        # error for invalid credentials
        print_markdown("## Invalid credentials")
        print_markdown("Please check your credentials in the config.toml file")

        shutdown()

        # todo error
