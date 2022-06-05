from utils.console import print_markdown
from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video
from dotenv import load_dotenv
import os, time, shutil

REQUIRED_VALUES = ["REDDIT_CLIENT_ID","REDDIT_CLIENT_SECRET","REDDIT_USERNAME","REDDIT_PASSWORD", "OPACITY"]

print_markdown(
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue."
)

time.sleep(3)

load_dotenv()

configured = True

if not os.path.exists(".env"):
    shutil.copy(".env.template", ".env")
    configured = False

for val in REQUIRED_VALUES:
    if val not in os.environ or not os.getenv(val):
        print(f"Please set the variable \"{val}\" in your .env file.")
        configured = False

try:
    float(os.getenv("OPACITY"))
except:
    print(f"Please ensure that OPACITY is set between 0 and 1 in your .env file")
    configured = False

if configured:
    reddit_object = get_subreddit_threads()
    length, number_of_comments = save_text_to_mp3(reddit_object)
    download_screenshots_of_reddit_posts(reddit_object, number_of_comments, os.getenv("THEME", "light"))
    download_background()
    chop_background_video(length)
    final_video = make_final_video(number_of_comments)
