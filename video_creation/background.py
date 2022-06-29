import random
from os import listdir, environ
from pathlib import Path
from random import randrange
import shutil
from pytube import YouTube
import re
import os
from random import randrange
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

from utils.console import print_step, print_substep


def get_start_and_end_times(video_length: int, length_of_clip: int) -> tuple[int, int]:
    """Generates a random interval of time to be used as the beckground of the video.

    Args:
        video_length (int): Length of the video
        length_of_clip (int): Length of the video to be used as the background

    Returns:
        tuple[int,int]: Start and end time of the randomized interval
    """
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def download_background(background: str):
    """Downloads given link, or if it's a path, copies that file over to assets/backgrounds/

    Args:
        background (str): Youtube link or file path
    """
    yt_id_pattern = re.compile(
        pattern=r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})')

    Path("./assets/backgrounds/").mkdir(parents=True, exist_ok=True)
    background_options = {
        "https://www.youtube.com/watch?v=n_Dv4JMiwK8",
        # "https://www.youtube.com/watch?v=2X9QGY__0II",
    }

    if Path(background).is_file():  # If background is a file
        shutil.copyfile(background, 'assets/backgrounds')

    # If background has a youtube video id, so if it's a youtube link
    elif re.findall(yt_id_pattern, background, re.IGNORECASE):

        background_options.add(background)

        # note: make sure the file name doesn't include an - in it
        if len(listdir("./assets/backgrounds")) < len(
            background_options
        ):  # if there are any background videos not installed
            print_step(
                "We need to download the backgrounds videos. they are fairly large but it's only done once. 😎"
            )
            print_substep(
                "Downloading the backgrounds videos... please be patient 🙏 ")
            for link in background_options:

                filename = re.match(yt_id_pattern, link, re.IGNORECASE).string

                if not Path(f"assets/backgrounds/{filename}").is_file():
                    print_substep(f"Downloading {filename} from {link}")
                    YouTube(link).streams.filter(res="1080p").first().download(
                        "assets/backgrounds", filename=f"{filename}"
                    )

            print_substep(
                "Background videos downloaded successfully! 🎉", style="bold green"
            )
            os.remove("assets/mp4/background.mp4")

    else:
        raise Exception("You didn't input a proper link into -b")


def chop_background_video(video_length: int):
    """Generates the background footage to be used in the video and writes it to assets/temp/background.mp4

    Args:
        video_length (int): Length of the clip where the background footage is to be taken out of
    """
    print_step("Finding a spot in the backgrounds video to chop...✂️")
    choice = random.choice(listdir("assets/backgrounds"))
    environ["background_credit"] = choice.split("-")[0]

    background = VideoFileClip(f"assets/backgrounds/{choice}")

    start_time, end_time = get_start_and_end_times(
        video_length, background.duration)
    ffmpeg_extract_subclip(
        f"assets/backgrounds/{choice}",
        start_time,
        end_time,
        targetname="assets/temp/background.mp4",
    )
    print_substep("Background video chopped successfully!", style="bold green")
