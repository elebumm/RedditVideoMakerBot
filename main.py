from reddit.askreddit import get_askreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--RedditID", help="ID of AskReddit thread to fetch") #This is an optional argument for specifiying the Reddit thread that you want
parser.add_argument("--VideoID", help="ID of Youtube video to fetch") #This is an optional argument for specifiying the YouTube video that you want
args = parser.parse_args()
reddit_object = get_askreddit_threads(args.RedditID)
length, number_of_comments = save_text_to_mp3(reddit_object)
download_screenshots_of_reddit_posts(reddit_object, number_of_comments)
download_background(args.VideoID)
chop_background_video(length, args.VideoID)
final_video = make_final_video(number_of_comments)
