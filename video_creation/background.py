import random
from os import listdir, environ, remove
from pathlib import Path
from random import randrange

from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from yt_dlp import YoutubeDL

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

        for uri, filename, credit in background_options:
            filename = f"{credit}-{filename}"
            ydl_opts = {'outtmpl': f'assets/backgrounds/_raw_{filename}', 'merge_output_format': 'mp4', }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(uri)
            videoclip = VideoFileClip(f"assets/backgrounds/{filename}")
            new_clip = videoclip.without_audio()
            new_clip.write_videofile(f"assets/backgrounds/{filename}")
            remove(f'assets/backgrounds/_raw_{filename}')

        print_substep("Background videos downloaded successfully! 🎉", style="bold green")


def chop_background_video(video_length):
    print_step("Finding a spot in the background video to chop...")
    choice = random.choice(listdir('assets/backgrounds'))
    environ["background_credit"] = choice.split('-')[0]
    background = VideoFileClip(f"assets/backgrounds/{choice}")
    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    print_substep(choice)
    ffmpeg_extract_subclip(
        f"assets/backgrounds/{choice}",
        start_time,
        end_time,
        targetname="assets/temp/background.mp4",
    )
    print_substep("Background video chopped successfully!", style="bold green")
