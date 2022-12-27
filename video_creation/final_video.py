#!/usr/bin/env python3
import multiprocessing
import os
import re
from os.path import exists
from typing import Tuple, Any
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from rich.console import Console

import ffmpeg
import shutil

from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.video import Video
from utils.videos import save_data
from utils import settings

console = Console()
W, H = 1080, 1920


def name_normalize(name: str) -> str:
    name = re.sub(r'[?\\"%*:|<>]', "", name)
    name = re.sub(r"( [w,W]\s?\/\s?[o,O,0])", r" without", name)
    name = re.sub(r"( [w,W]\s?\/)", r" with", name)
    name = re.sub(r"(\d+)\s?\/\s?(\d+)", r"\1 of \2", name)
    name = re.sub(r"(\w+)\s?\/\s?(\w+)", r"\1 or \2", name)
    name = re.sub(r"\/", r"", name)
    name[:30]

    lang = settings.config["reddit"]["thread"]["post_lang"]
    if lang:
        import translators as ts

        print_substep("Translating filename...")
        translated_name = ts.google(name, to_language=lang)
        return translated_name

    else:
        return name



def make_final_video(
    number_of_clips: int,
    length: int,
    reddit_obj: dict,
    background_config: Tuple[str, str, str, Any],
):
    """Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp
    Args:
        number_of_clips (int): Index to end at when going through the screenshots'
        length (int): Length of the video
        reddit_obj (dict): The reddit object that contains the posts to read.
        background_config (Tuple[str, str, str, Any]): The background config to use.
    """
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    print_step("Creating the final video 🎥")

    # Gather all audio clips
    audio_clips = [ffmpeg.input(f"assets/temp/{id}/mp3/{i}.mp3") for i in range(number_of_clips)]
    audio_clips.insert(0, ffmpeg.input(f"assets/temp/{id}/mp3/title.mp3"))
    
    audio_clips_durations = [float(ffmpeg.probe(f"assets/temp/{id}/mp3/{i}.mp3")['format']['duration']) for i in range(number_of_clips)]
    audio_clips_durations.insert(0, float(ffmpeg.probe(f"assets/temp/{id}/mp3/title.mp3")['format']['duration']))
    audio_concat = ffmpeg.concat(*audio_clips, a=1, v=0)
    ffmpeg.output(audio_concat, f"assets/temp/{id}/audio.mp3").overwrite_output().run()

    console.log(f"[bold green] Video Will Be: {length} Seconds Long")

    # Remove the audio from the background video and crop it
    ffmpeg.input(f"assets/temp/{id}/background.mp4").filter('crop', "ih*(9/16)", "ih").output(f"assets/temp/{id}/background_noaudio.mp4", an=None, **{"c:v": "h264"}).overwrite_output().run()

    audio = ffmpeg.input(f"assets/temp/{id}/audio.mp3")
    video = ffmpeg.input(f"assets/temp/{id}/background_noaudio.mp4")

    # Gather all images
    image_clips = list()
    image_clips.insert(
        0,
        ffmpeg.input(f"assets/temp/{id}/png/title.png")['v']
        .filter('scale', 'iw-200', -1)
    )

    current_time = 0
    for i in range(0, number_of_clips + 1):
        image_clips.append(
            ffmpeg.input(f"assets/temp/{id}/png/comment_{i}.png")['v']
            .filter('scale', 'iw-200', -1)
        )
        video = video.overlay(image_clips[i], enable=f'between(t,{current_time},{current_time + audio_clips_durations[i]})', x='(main_w-overlay_w)/2', y='(main_h-overlay_h)/2')
        current_time += audio_clips_durations[i]
    
    title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])
    idx = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    filename = f"{name_normalize(title)[:251]}.mp4"
    subreddit = settings.config["reddit"]["thread"]["subreddit"]

    if not exists(f"./results/{subreddit}"):
        print_substep("The results folder didn't exist so I made it")
        os.makedirs(f"./results/{subreddit}")

    output = ffmpeg.output(video, audio, f"results/{subreddit}/{filename}", f='mp4', **{"c:v": "h264"}).overwrite_output()
    output.run()

    save_data(subreddit, filename, title, idx, background_config[2])
    print_step("Removing temporary files 🗑")
    cleanups = cleanup(id)
    print_substep(f"Removed {cleanups} temporary files 🗑")
    print_substep("See result in the results folder!")

    print_step(
        f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {background_config[2]}'
    )
