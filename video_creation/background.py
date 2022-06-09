#!/usr/bin/env python3
from random import randrange

from yt_dlp import YoutubeDL

from pathlib import Path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from utils.console import print_step, print_substep
from moviepy.video.io.VideoFileClip import VideoFileClip
import datetime


def get_start_and_end_times(video_length, length_of_clip):

    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length

def download_background(video_length):

    """Downloads the background video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
    """

    print_substep("\nPut the URL of the video you want in the background.\nThe default video is a Minecraft parkour video.\n"
        "Leave the input field blank to use the default.")
    print_substep(f"Make sure the video is longer than {str(datetime.timedelta(seconds=round(video_length + 180)))}!\n", style="red")

    inp = input("URL: ")

    if not inp:
        vidurl = "https://www.youtube.com/watch?v=n_Dv4JMiwK8"
    else:
        vidurl = inp

    vidpath = vidurl.split("v=")[1]

    if not Path(f"assets/mp4/{vidpath}.mp4").is_file():
        print_step(
            "We need to download the background video. This may be fairly large but it's only done once per background."
        )

        print_substep("Downloading the background video... please be patient.")

        ydl_opts = {
            "outtmpl": f"assets/mp4/{vidpath}.mp4",
            "merge_output_format": "mp4",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(vidurl)

        print_substep("Background video downloaded successfully!", style="bold green")
        
    return vidpath


def chop_background_video(video_length, vidpath):
    print_step("Finding a spot in the background video to chop...")
    background = VideoFileClip(f"assets/mp4/{vidpath}.mp4")
    if background.duration < video_length + 180:
        print_substep("This video is too short.", style="red")
        noerror = False
        return noerror
    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    
    with VideoFileClip("assets/mp4/background.mp4") as video:
        new = video.subclip(start_time, end_time)
        new.write_videofile("assets/mp4/clip.mp4")
        

    print_substep("Background video chopped successfully!", style="bold green")
    noerror = True
    return noerror
