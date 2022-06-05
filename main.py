from unittest.util import _MAX_LENGTH
from utils.console import print_markdown
from utils.console import print_step
import time

from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video
import random
from dotenv import load_dotenv
import os

print_markdown(
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue. \n ### This modified version of this tool was created by [@tya.design](https://tya.design) and is available on [GitHub](https://github.com/Tyaaa-aa/RedditVideoMakerBot)."
)

time.sleep(3)

# The maximum length of the video in seconds. (This is the length of the video that will be created, but not 100% accurate)
MAX_LENGTH = 55

# Video speed multiplier (1.0 = normal speed, 2.0 = double speed, 0.5 = half speed)
VIDEO_SPEED = 1.2

# Voice accent https://gtts.readthedocs.io/en/latest/module.html?highlight=accent
VOICE_ACCENT = "co.uk"

# Background video to use (video id from youtube)
# Use an array of videos to create a random background video

BACKGROUND_VIDEO_ARRAY = ["5sYdvjXX7YU", "Pt5_GSKIWQM", "uVKxtdMgJVU","E-8JlyO59Io","cEXWuxP1cW0","aeiAt1lFkGg","r9QzNn25SDs","vVJuMq1CMNo","xVqwTUTOOWg","U0By6YNp2C4"]
# select random 1
BACKGROUND_VIDEO = BACKGROUND_VIDEO_ARRAY[random.randrange(0, len(BACKGROUND_VIDEO_ARRAY))]



reddit_object = get_subreddit_threads()
video_title = reddit_object["thread_title"]
chosen_subreddit = reddit_object["subreddit"]
ffmpeg_exe = reddit_object["ffmpeg_exe"]

load_dotenv()
length, number_of_comments = save_text_to_mp3(reddit_object, MAX_LENGTH, VOICE_ACCENT)
download_screenshots_of_reddit_posts(reddit_object, number_of_comments, os.getenv("THEME"))
download_background(BACKGROUND_VIDEO)
chop_background_video(BACKGROUND_VIDEO, length)
final_video = make_final_video(number_of_comments, chosen_subreddit, video_title, ffmpeg_exe, VIDEO_SPEED)
