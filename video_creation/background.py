from random import randrange

from yt_dlp import YoutubeDL

from pathlib import Path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from utils.console import print_step, print_substep


def get_start_and_end_times(video_length, length_of_clip):

    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length

def download_background():
    """Downloads the background video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
    """

    if not Path("assets/mp4/background.mp4").is_file():
        print_step(
            "We need to download the Minecraft background video. This is fairly large but it's only done once."
        )

        print_substep("Downloading the background video... please be patient.")

        ydl_opts = {
            "outtmpl": "assets/mp4/background.mp4",
            "merge_output_format": "mp4",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download("https://www.youtube.com/watch?v=n_Dv4JMiwK8")

        print_substep("Background video downloaded successfully!", style="bold green")


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
