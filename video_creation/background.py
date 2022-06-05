from random import randrange

from yt_dlp import YoutubeDL

from pathlib import Path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from utils.console import print_step, print_substep

def get_start_and_end_times(video_length, length_of_clip):

    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length

def download_background(youtube_id):
    if not Path(f"assets/mp4/background-{youtube_id}.mp4").is_file():
        print_step(
            "We need to download the background video. This is fairly large but it's only done once per video."
        )

        print_substep("Downloading the background video...")

        ydl_opts = {
            "outtmpl": f"assets/mp4/background-{youtube_id}.mp4",
            "merge_output_format": "mp4",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(f"https://www.youtube.com/watch?v={youtube_id}")

        print_substep("Background video downloaded successfully!", style="bold green")


def chop_background_video(youtube_id, video_length):
    print_step("Finding a spot in the background video to chop...")
    background_path = f"assets/mp4/background-{youtube_id}.mp4"
    background = VideoFileClip(background_path)

    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    ffmpeg_extract_subclip(
        background_path,
        start_time,
        end_time,
        targetname="assets/mp4/clip.mp4",
    )
    print_substep("Background video chopped successfully!", style="bold green")
