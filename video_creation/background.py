from random import randrange
from pytube import YouTube
from pathlib import Path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from utils.console import print_step, print_substep


def get_start_and_end_times(video_length, length_of_clip):

    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def download_background(videoID):
    """Downloads the background video from youtube.

    Shoutout to: bbswitzer (https://www.youtube.com/watch?v=n_Dv4JMiwK8)
    """
    if not videoID:
        print_step(
            "Shoutout to bbswitzer for his Minecraft parkour "
        )
        videoID = "n_Dv4JMiwK8"
    url = "https://www.youtube.com/watch?v={}".format(videoID)

    if not Path("assets/mp4/{}.mp4".format(videoID)).is_file():
        print_step(
            "We need to download the background video. This is fairly large but it's only done once. 😎"
        )
        print_substep("Downloading the background video... please be patient 🙏")
        YouTube(url).streams.filter(
            res="720p"
        ).first().download(
            "assets/mp4",
            filename="{}.mp4".format(videoID),
        )
        print_substep("Background video downloaded successfully! 🎉", style="bold green")


def chop_background_video(video_length, videoID):
    print_step("Finding a spot in the background video to chop...✂️")
    if not videoID:
        videoID = "n_Dv4JMiwK8"
    background = VideoFileClip("assets/mp4/{}.mp4".format(videoID))

    start_time, end_time = get_start_and_end_times(video_length, background.duration)
    ffmpeg_extract_subclip(
        "assets/mp4/{}.mp4".format(videoID),
        start_time,
        end_time,
        targetname="assets/mp4/clip.mp4",
    )
    print_substep("Background video chopped successfully! 🎉", style="bold green")
