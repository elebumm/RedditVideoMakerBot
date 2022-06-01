from random import randrange, choice
from pytube import YouTube
from pathlib import Path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from utils.console import print_step, print_substep
from urllib import parse


def get_start_and_end_times(video_length, length_of_clip):

    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def download_background():
    """Downloads the background video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
    """
    # List of choices for the background video
    background_choices = [
        "https://www.youtube.com/watch?v=n_Dv4JMiwK8",
        "https://www.youtube.com/watch?v=oCtokDlLbCU",
    ]

    video_id = parse.parse_qs(parse.urlsplit(choice(background_choices)).query)["v"][0]

    if not Path(f"assets/mp4/{video_id}.mp4").is_file():
        print_step(
            "We need to download the Minecraft background video. This is fairly large but it's only done once. 😎"
        )
        print_substep("Downloading the background video... please be patient 🙏")
        YouTube(f"https://www.youtube.com/watch?v={video_id}").streams.filter(
            res="720p"
        ).first().download(
            "assets/mp4",
            filename=f"{video_id}.mp4",
        )
        print_substep("Background video downloaded successfully! 🎉", style="bold green")

    return video_id


def chop_background_video(video_length, video_id):
    print_step("Finding a spot in the background video to chop...✂️")
    background = VideoFileClip(f"assets/mp4/{video_id}.mp4")

    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    ffmpeg_extract_subclip(
        f"assets/mp4/{video_id}.mp4",
        start_time,
        end_time,
        targetname="assets/mp4/clip.mp4",
    )
    print_substep("Background video chopped successfully! 🎉", style="bold green")
