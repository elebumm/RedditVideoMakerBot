import random
from os import listdir, environ
from pathlib import Path
from random import randrange
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from rich.progress import Progress

from utils.console import print_step, print_substep


def get_start_and_end_times(video_length, length_of_clip):
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def download_background():
    """Downloads the backgrounds/s video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
    Shoutout to: Orbital Gameplay (https://www.youtube.com/watch?v=2X9QGY__0II)
    """
    Path("./assets/backgrounds/").mkdir(parents=True, exist_ok=True)
    background_options = [  # uri , filename , credit
        ("https://www.youtube.com/watch?v=n_Dv4JMiwK8", "parkour.mp4", 'bbswitzer'),
        ("https://www.youtube.com/watch?v=2X9QGY__0II", "rocket_league.mp4", 'Orbital Gameplay'), ]
    # note: make sure the file name doesn't include a - in it
    if len(listdir('./assets/backgrounds')) != len(
            background_options):  # if there are any background videos not installed
        print_step("We need to download the backgnrounds videos. they are fairly large but it's only done once. 😎")
        print_substep("Downloading the backgrounds videos... please be patient 🙏 ")
        with Progress() as progress:

            download_task = progress.add_task("[green]Downloading...", total=2)

            for uri, filename, credit in background_options:
                print_substep(f"Downloading {filename} from {uri}")
                YouTube(uri).streams.filter(res="720p").first().download("assets/backgrounds",
                                                                         filename=f"{credit}-{filename}")
                progress.update(download_task, advance=1)

        print_substep("Background videos downloaded successfully! 🎉", style="bold green")


def chop_background_video(video_length):
    print_step("Finding a spot in the backgrounds video to chop...✂️")
    choice = random.choice(listdir('assets/backgrounds'))
    environ["background_credit"] = choice.split('-')[0]

    background = VideoFileClip(f"assets/backgrounds/{choice}")

    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    ffmpeg_extract_subclip(f'assets/backgrounds/{choice}', start_time, end_time,
                           targetname="assets/temp/backgrounds.mp4", )
    print_substep("Background video chopped successfully! 🎉", style="bold green")
