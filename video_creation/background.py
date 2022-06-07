import re
import os
from random import randrange

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
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

    print_step("Downloading the background video.")
    ydl_opts = {
        "outtmpl": "assets/mp4/background.mp4",
        "merge_output_format": "mp4",
        "retries": 3,
    }

    background_check = os.path.isfile("assets/mp4/background.mp4")
    if background_check and background is not None:
        print_substep(
            "Background video is already downloaded! Replacing ...", style_="bold red"
        )
        os.remove("assets/mp4/background.mp4")

    cancel = True
    try:
        with YoutubeDL(ydl_opts) as ydl:
            if background is None:
                ydl.download("https://www.youtube.com/watch?v=n_Dv4JMiwK8")
            elif background is not None:
                check_link = re.match(
                    "(?:https?:\/\/)?(?:www\.)?youtu(?:\.be\/|be.com\/"
                    + "\S*(?:watch|embed)(?:(?:(?=\/[-a-zA-Z0-9_]{11,}(?!"
                    + "\S))\/)|(?:\S*v=|v\/)))([-a-zA-Z0-9_]{11,})"
                    , background.strip()
                )

                if check_link:
                    print_substep(f"Downloading video from: {background}", style_="bold")
                    ydl.download(background)
                elif re.match(background[-4], "mp4"):
                    print_substep(f"Using the given video file: {background}", style_="bold")
                    os.replace(background.strip(), "assets/mp4/background.mp4")
                else: # if the link is not youtube link or  a file
                    raise ValueError
    except ValueError:
        print_substep("Invalid input!", style_="bold red")
    except ConnectionError:
        print_substep("There is a connection error!", style_="bold red")
    except DownloadError:
        print_substep("There is a download error!", style_="bold red")
    else:
        print_substep("Background video downloaded successfully!", style_="bold green")
        cancel = False

        if cancel:
            # to prevent further error and processes from happening
            raise SystemExit()


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
    print_substep("Background video chopped successfully!", style_="bold green")
