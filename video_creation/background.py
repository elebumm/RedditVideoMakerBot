import json
import random
import re
from pathlib import Path
from random import randrange
from typing import Any, Tuple

import yt_dlp
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from utils import settings
from utils.console import print_step, print_substep

# Load background video configurations from the JSON file
with open("./utils/backgrounds.json") as json_file:
    background_options = json.load(json_file)

# Remove any comments from the JSON file
background_options.pop("__comment", None)

# Set the position of the background video in the final output
for name in list(background_options.keys()):
    pos = background_options[name][3]

    if pos != "center":
        background_options[name][3] = lambda t: ("center", pos + t)

# Function to generate a random start and end time for the background video
def get_start_and_end_times(video_length: int, length_of_clip: int) -> Tuple[int, int]:
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length

# Function to get the background configuration from the settings
def get_background_config():
    try:
        choice = str(
            settings.config["settings"]["background"]["background_choice"]
        ).casefold()
    except AttributeError:
        print_substep("No background selected. Picking random background'")
        choice = None

    if not choice or choice not in background_options:
        choice = random.choice(list(background_options.keys()))

    return background_options[choice]

# Function to download the background video from YouTube
def download_background(background_config: Tuple[str, str, str, Any]):
    Path("./assets/backgrounds/").mkdir(parents=True, exist_ok=True)
    uri, filename, credit, _ = background_config
    if Path(f"assets/backgrounds/{credit}-{filename}").is_file():
        return
    print_step(
        "We need to download the backgrounds videos. they are fairly large but it's only done once. 😎"
    )
    print_substep("Downloading the backgrounds videos... please be patient 🙏 ")
    print_substep(f"Downloading {filename} from {uri}")

    # Set the download option for yt-dlp
    ydl_opts = {
        'outtmpl': f'assets/backgrounds/{credit}-{filename}',
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]'
    }

    # Download the video with yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([uri])

    print_substep("Background video downloaded successfully! 🎉", style="bold green")


def chop_background_video(
    background_config: Tuple[str, str, str, Any], video_length: int, reddit_object: dict
):
    print_step("Finding a spot in the backgrounds video to chop...✂️")
    choice = f"{background_config[2]}-{background_config[1]}"
    id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])

    # Load the background video
    background = VideoFileClip(f"assets/backgrounds/{choice}")

    # Get the start and end times for the portion to extract
    start_time, end_time = get_start_and_end_times(video_length, background.duration)

    # Extract the portion of the video
    try:
        ffmpeg_extract_subclip(
            f"assets/backgrounds/{choice}",
            start_time,
            end_time,
            targetname=f"assets/temp/{id}/background.mp4",
        )
    except (OSError, IOError):  # ffmpeg issue see #348
        print_substep("FFMPEG issue. Trying again...")
        with VideoFileClip(f"assets/backgrounds/{choice}") as video:
            new = video.subclip(start_time, end_time)
            new.write_videofile(f"assets/temp/{id}/background.mp4")
    
    # Output a success message
    print_substep("Background video chopped successfully!", style="bold green")
    return background_config[2]
