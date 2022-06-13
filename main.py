import time

from subprocess import Popen
from dotenv import load_dotenv
from os import getenv, name
from reddit.subreddit import get_subreddit_threads
from utils.cleanup import cleanup
from utils.console import print_markdown, print_step
from video_creation.background import download_background, chop_background_video
from video_creation.final_video import make_final_video
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.voices import save_text_to_mp3

banner = """
██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗ 
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║███████╗██████╔╝██████╔╝██║   ██║        ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝         ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
print(banner)
load_dotenv()
# base code by elebumm
print_markdown(
    "### Thanks for using this tool! 😊 Feel free to contribute to this project on GitHub! (JasonLovesDoggo/RedditVideoMakerBot). If you have any questions, feel free to reach out to me on Twitter @JasonLovesDoggo or submit a GitHub issue."
)

time.sleep(2)

client_id = getenv("REDDIT_CLIENT_ID")
client_secret = getenv("REDDIT_CLIENT_SECRET")
username = getenv("REDDIT_USERNAME")
password = getenv("REDDIT_PASSWORD")
reddit2fa = getenv("REDDIT_2FA")


def main():
    cleanup()

    def get_obj():
        reddit_obj = get_subreddit_threads()
        return reddit_obj

    reddit_object = get_obj()
    length, number_of_comments = save_text_to_mp3(reddit_object)
    download_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    download_background()
    chop_background_video(length)
    final_video = make_final_video(number_of_comments, length)


def run_many(times):
    for x in range(times):
        x = x + 1
        print_step(
            f'on the {x}{("st" if x == 1 else ("nd" if x == 2 else ("rd" if x == 3 else "th")))} iteration of {times}'
        )  # correct 1st 2nd 3rd 4th 5th....
        main()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


if __name__ == "__main__":
    try:
        if getenv("TIMES_TO_RUN") and isinstance(int(getenv("TIMES_TO_RUN")), int):
            run_many(int(getenv("TIMES_TO_RUN")))
        else:
            main()
    except KeyboardInterrupt:
        print_markdown("## Clearing temp files")
        cleanup()
        exit()
