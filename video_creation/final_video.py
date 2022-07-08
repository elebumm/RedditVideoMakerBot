#!/usr/bin/env python3
import multiprocessing
import os
import re
from os.path import exists
from typing import Tuple, Any
import translators as ts

from moviepy.editor import (VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips, concatenate_audioclips,
                            CompositeAudioClip, CompositeVideoClip, )
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio, ffmpeg_extract_subclip
from rich.console import Console
import moviepy.editor as mpe

from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.videos import save_data
from utils import settings

console = Console()
VOLUME_MULTIPLIER = settings.config["settings"]['background']["background_audio_volume"]
W, H = 1080, 1920


def name_normalize(name: str) -> str:
    name = re.sub(r'[?\\"%*:|<>]', "", name)
    name = re.sub(r"( [w,W]\s?\/\s?[o,O,0])", r" without", name)
    name = re.sub(r"( [w,W]\s?\/)", r" with", name)
    name = re.sub(r"(\d+)\s?\/\s?(\d+)", r"\1 of \2", name)
    name = re.sub(r"(\w+)\s?\/\s?(\w+)", r"\1 or \2", name)
    name = re.sub(r"\/", r"", name)

    lang = settings.config["reddit"]["thread"]["post_lang"]
    if lang:
        print_substep("Translating filename...")
        translated_name = ts.google(name, to_language=lang)
        return translated_name

    else:
        return name


def make_final_video(number_of_clips: int, length: int, reddit_obj: dict, background_config: Tuple[str, str, str, Any]):
    """Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp
    Args:
        number_of_clips (int): Index to end at when going through the screenshots'
        length (int): Length of the video
        reddit_obj (dict): The reddit object that contains the posts to read.
        background_config (Tuple[str, str, str, Any]): The background config to use.
    """
    print_step("Creating the final video 🎥")
    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)
    opacity = settings.config["settings"]["opacity"]
    background_clip = (
        VideoFileClip("assets/temp/background.mp4").without_audio().resize(height=H).crop(x1=1166.6, y1=0, x2=2246.6,
                                                                                          y2=1920))

    # Gather all audio clips
    audio_clips = [AudioFileClip(f"assets/temp/mp3/{i}.mp3") for i in range(number_of_clips)]
    audio_clips.insert(0, AudioFileClip("assets/temp/mp3/title.mp3"))
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])

    console.log(f"[bold green] Video Will Be: {length} Seconds Long")
    # add title to video
    image_clips = []
    # Gather all images
    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)
    image_clips.insert(0, ImageClip("assets/temp/png/title.png").set_duration(audio_clips[0].duration).resize(
        width=W - 100).set_opacity(new_opacity), )

    for i in range(0, number_of_clips):
        image_clips.append(
            ImageClip(f"assets/temp/png/comment_{i}.png").set_duration(audio_clips[i + 1].duration).resize(
                width=W - 100).set_opacity(new_opacity))

    # if os.path.exists("assets/mp3/posttext.mp3"):
    #    image_clips.insert(
    #        0,
    #        ImageClip("assets/png/title.png")
    #        .set_duration(audio_clips[0].duration + audio_clips[1].duration)
    #        .set_position("center")
    #        .resize(width=W - 100)
    #        .set_opacity(float(opacity)),
    #    )
    # else: story mode stuff
    img_clip_pos = background_config[3]
    image_concat = concatenate_videoclips(image_clips).set_position(img_clip_pos)
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])
    title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])
    idx = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    filename = f"{name_normalize(title)}.mp4"
    subreddit = settings.config["reddit"]["thread"]["subreddit"]

    save_data(subreddit, filename, title, idx, background_config[2])

    if not exists(f"./results/{subreddit}"):
        print_substep("The results folder didn't exist so I made it")
        os.makedirs(f"./results/{subreddit}")

    final.write_videofile("assets/temp/temp.mp4", fps=30, audio_codec="aac", audio_bitrate="192k", verbose=False,
                          threads=multiprocessing.cpu_count(), )
    if settings.config["settings"]['background']["background_audio"] and exists(f"assets/backgrounds/background.mp3"):
        if not isinstance(VOLUME_MULTIPLIER, float):
            print("No background audio volume set, using default of .3 set it in the config.toml file")
            assert VOLUME_MULTIPLIER == float(0.3)
        print('Merging background audio with video')
        my_clip = mpe.VideoFileClip('assets/temp/temp.mp4')
        audio_background = AudioFileClip("assets/backgrounds/background.mp3")
        lowered_audio = audio_background.multiply_volume(
            VOLUME_MULTIPLIER)  # lower volume by background_audio_volume, use with fx
        lowered_audio = lowered_audio.subclip(0, my_clip.duration)  # trim the audio to the length of the video
        lowered_audio.set_duration(my_clip.duration)  # set the duration of the audio to the length of the video
        final_audio = mpe.CompositeAudioClip([my_clip.audio, lowered_audio])
        final_clip = my_clip.set_audio(final_audio)

        final_clip.write_videofile("assets/temp/temp_audio.mp4", fps=30, audio_codec="aac", audio_bitrate="192k",
                                   verbose=False, threads=multiprocessing.cpu_count())
        ffmpeg_extract_subclip(  # check if this gets run
            "assets/temp/temp_audio.mp4", 0, final.duration, targetname=f"results/{subreddit}/{filename}", )
    else:
        ffmpeg_extract_subclip("assets/temp/temp.mp4", 0, final.duration,
                               targetname=f"results/{subreddit}/{filename}", )
    print_step("Removing temporary files 🗑")
    cleanups = cleanup()
    print_substep(f"Removed {cleanups} temporary files 🗑")
    print_substep("See result in the results folder!")

    print_step(f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {background_config[2]}')
