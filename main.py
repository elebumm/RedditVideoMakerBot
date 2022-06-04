from utils.console import print_markdown
import time

from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video
from dotenv import load_dotenv
import os
import re
import math


def next_name(dir="output/"):
    i = 0
    for path in os.listdir(dir):
        if path.endswith(".mp4"):
            name = path.split(".")[0]
            if name.isdigit():
                name = int(name)
                if i < name + 1:
                    i = name + 1
    return i


print_markdown(
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue."
)

time.sleep(3)
load_dotenv()

for thread_number in range(int(os.getenv("LIMIT"))):
    reddit_object = get_subreddit_threads(thread_number)

    thread_title = str.strip(reddit_object["thread_title"]).replace(" ", "_")
    thread_title = re.sub(r"[^_\w]", "", thread_title)
    thread_url_elements = reddit_object['thread_url'].split('/')
    file_name = f"{thread_url_elements[4]}-{thread_url_elements[6]}"
    file_exists = os.path.isfile(f"output/{file_name}.mp4")
    fail_exists = os.path.isfile(f"output/fail/{file_name}")

    if file_exists is False and fail_exists is False:
        length, number_of_comments = save_text_to_mp3(reddit_object)
        if length >= int(os.getenv("MIN_VID")) and number_of_comments > 0:
            print(f"Video is {math.ceil(length)}s long with {number_of_comments} comments.")
            download_screenshots_of_reddit_posts(reddit_object, number_of_comments, os.getenv("THEME"))
            download_background()
            chop_background_video(length)
            final_video = make_final_video(number_of_comments, name=file_name, length=length)
        else:
            print("Content too short! Trying again...")
            open(f"output/fail/{file_name}", "w+").close()
    else:
        print(f"Video for thread already exists! Trying again...")

    if os.getenv("LOOP") != "yes":
        break