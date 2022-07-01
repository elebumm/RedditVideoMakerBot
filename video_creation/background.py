import random
from os import listdir, environ
from pathlib import Path
from random import randrange

from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from pytube import YouTube

from utils.console import print_step, print_substep


def get_start_and_end_times(video_length: int, length_of_clip: int) -> tuple[int, int]:
    """Generates a random interval of time to be used as the background of the video.

    Args:
        video_length (int): Length of the video
        length_of_clip (int): Length of the video to be used as the background

    Returns:
        tuple[int,int]: Start and end time of the randomized interval
    """
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def download_background():
    """Downloads the backgrounds/s video from YouTube."""
    Path("./assets/backgrounds/").mkdir(parents=True, exist_ok=True)
    background_options = [  # uri , filename , credit
        ("https://www.youtube.com/watch?v=n_Dv4JMiwK8", "parkour.mp4", "bbswitzer"),
        # (
        #    "https://www.youtube.com/watch?v=2X9QGY__0II",
        #    "rocket_league.mp4",
        #    "Orbital Gameplay",
        # ),
    ]
    # note: make sure the file name doesn't include an - in it
    if not len(listdir("./assets/backgrounds")) >= len(
        background_options
    ):  # if there are any background videos not installed
        print_step(
            "We need to download the backgrounds videos. they are fairly large but it's only done once. 😎"
        )
        print_substep("Downloading the backgrounds videos... please be patient 🙏 ")
        for uri, filename, credit in background_options:
            if Path(f"assets/backgrounds/{credit}-{filename}").is_file():
                continue  # adds check to see if file exists before downloading
            print_substep(f"Downloading {filename} from {uri}")
            YouTube(uri).streams.filter(res="1080p").first().download(
                "assets/backgrounds", filename=f"{credit}-{filename}"
            )

        print_substep("Background videos downloaded successfully! 🎉", style="bold green")


def chop_background_video(video_length: int):
    """Generates the background footage to be used in the video and writes it to assets/temp/background.mp4

    Args:
        video_length (int): Length of the clip where the background footage is to be taken out of
    """
    print_step("Finding a spot in the backgrounds video to chop...✂️")
    choice = random.choice(listdir("assets/backgrounds"))
    environ["background_credit"] = choice.split("-")[0]

    background = VideoFileClip(f"assets/backgrounds/{choice}")

    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    try:
        ffmpeg_extract_subclip(
            f"assets/backgrounds/{choice}",
            start_time,
            end_time,
            targetname="assets/temp/background.mp4",
        )
    except (OSError, IOError):  # ffmpeg issue see #348
        print_substep("FFMPEG issue. Trying again...")
        with VideoFileClip(f"assets/backgrounds/{choice}") as video:
            new = video.subclip(start_time, end_time)
            new.write_videofile("assets/temp/background.mp4")
    print_substep("Background video chopped successfully!", style="bold green")
