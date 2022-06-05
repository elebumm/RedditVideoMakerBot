import re
from random import randrange
from pathlib import Path

from yt_dlp import YoutubeDL
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

from utils.console import print_step, print_substep


def get_start_and_end_times(video_length, length_of_clip):
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def download_background(background):
    """Downloads the background video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
        """
    print_step( # removed minecraft, since the background can be changed according to user input.
        "Downloading the background video."
    )

    ydl_opts = {
        "outtmpl": "assets/mp4/background.mp4",
        "merge_output_format": "mp4",
    }

    background_check = Path("assets/mp4/background.mp4").is_file()
    if background is not None or not background_check:
        if background_check:
            print_substep("Background video is already downloaded! Replacing ...")

        try:
            with YoutubeDL(ydl_opts) as ydl:
                if background is None:
                    ydl.download("https://www.youtube.com/watch?v=n_Dv4JMiwK8")
                else:
                    if (
                            re.match("https://*youtube.com*", background)
                            and background is not None
                        ):
                        ydl.download(background)
                    else: # if the link is not youtube link
                        raise ValueError
        except (
                ValueError
                # add more exceptions
            ):
            print_substep("The given link is not accepted!", style="bold red")
        else:
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
