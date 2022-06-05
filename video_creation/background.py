from random import randrange

from yt_dlp import YoutubeDL

from pathlib import Path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from utils.console import print_step, print_substep
import requests

def get_start_and_end_times(video_length, length_of_clip):

    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length

def choose_bg(bg_video_path):
    print_step(
       "We need to download the background video. This is fairly large but it's only done once."
    )

    print_substep("Downloading the background video... please be patient.")

    ydl_opts = {
        "outtmpl": "assets/mp4/background.mp4",
        "merge_output_format": "mp4",
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(bg_video_path)

    # check if the link is reachable
    request = requests.get(bg_video_path, allow_redirects=False)
    if request.status_code >= 200:
        print_substep("Background video downloaded successfully!", style="bold green")
    else:
        print_substep("The link you've given might be broken or private, make sure the video can be accessed publicly")    


def download_background():
    """Downloads the background video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
    """
    get_bg_preference = input("The default background video is a Minecraft parkour, do you want to provide a custom video? (y/n)").lower()

    if not Path("assets/mp4/background.mp4").is_file() and get_bg_preference == "y":
        choose_bg(input("Please insert the YouTube link to your video: "))
    elif get_bg_preference == "n":
        print_substep("Downloading default Minecraft background! 👾")
        choose_bg("https://www.youtube.com/watch?v=n_Dv4JMiwK8")
    else:
        print_substep("Invalid input or you already have a background video downloaded, if so please delete the video before a retry", style="red")

def chop_background_video(video_length):
    print_step("Finding a spot in the background video to chop...")
    background = VideoFileClip("assets/mp4/background.mp4")

    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    ffmpeg_extract_subclip(
        "assets/mp4/background.mp4",
        start_time,
        end_time,
        targetname="assets/mp4/clip.mp4",
    )
    print_substep("Background video chopped successfully!", style="bold green")
