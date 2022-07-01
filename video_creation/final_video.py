#!/usr/bin/env python3
import multiprocessing
import os
import re
from os.path import exists

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
    CompositeVideoClip,
)
from moviepy.video.io import ffmpeg_tools
from rich.console import Console

from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.videos import save_data

console = Console()

W, H = 1080, 1920


def make_final_video(number_of_clips: int, length: int, reddit_obj: dict[str]):
    """Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp

    Args:
        number_of_clips (int): Index to end at when going through the screenshots
        length (int): Length of the video
    """
    print_step("Creating the final video 🎥")
    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)
    opacity = os.getenv("OPACITY")
    background_clip = (
        VideoFileClip("assets/temp/background.mp4")
        .without_audio()
        .resize(height=H)
        .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )

    # Gather all audio clips
    audio_clips = []
    for i in range(0, number_of_clips):
        audio_clips.append(AudioFileClip(f"assets/temp/mp3/{i}.mp3"))
    audio_clips.insert(0, AudioFileClip("assets/temp/mp3/title.mp3"))
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])

    # Get sum of all clip lengths
    total_length = sum([clip.duration for clip in audio_clips])
    # round total_length to an integer
    int_total_length = round(total_length)
    # Output Length

    console.log(f"[bold green] Video Will Be: {int_total_length} Seconds Long")
    # add title to video
    image_clips = []
    # Gather all images
    if opacity is None or float(opacity) >= 1:  # opacity not set or is set to one OR MORE
        image_clips.insert(
            0,
            ImageClip("assets/temp/png/title.png")
            .set_duration(audio_clips[0].duration)
            .set_position("center")
            .resize(width=W - 100),
        )
    else:
        image_clips.insert(
            0,
            ImageClip("assets/temp/png/title.png")
            .set_duration(audio_clips[0].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
        )

    for i in range(0, number_of_clips):
        if opacity is None or float(opacity) >= 1:  # opacity not set or is set to one OR MORE
            image_clips.append(
                ImageClip(f"assets/temp/png/comment_{i}.png")
                .set_duration(audio_clips[i + 1].duration)
                .set_position("center")
                .resize(width=W - 100),
            )
        else:
            image_clips.append(
                ImageClip(f"assets/temp/png/comment_{i}.png")
                .set_duration(audio_clips[i + 1].duration)
                .set_position("center")
                .resize(width=W - 100)
                .set_opacity(float(opacity)),
            )

    # if os.path.exists("assets/mp3/posttext.mp3"):
    #    image_clips.insert(
    #        0,
    #        ImageClip("assets/png/title.png")
    #        .set_duration(audio_clips[0].duration + audio_clips[1].duration)
    #        .set_position("center")
    #        .resize(width=W - 100)
    #        .set_opacity(float(opacity)),
    #    )
    # else:
    image_concat = concatenate_videoclips(image_clips).set_position(("center", "center"))
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])
    title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])
    idx = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    filename = f"{title}.mp4"
    subreddit = os.getenv("SUBREDDIT")

    save_data(filename, title, idx)

    if not exists(f"./results/{subreddit}"):
        print_substep("The results folder didn't exist so I made it")
        os.makedirs(f"./results/{subreddit}")

    final.write_videofile(
        "assets/temp/temp.mp4",
        fps=30,
        audio_codec="aac",
        audio_bitrate="192k",
        verbose=False,
        threads=multiprocessing.cpu_count(),
    )
    ffmpeg_tools.ffmpeg_extract_subclip(
        "assets/temp/temp.mp4", 0, length, targetname=f"results/{subreddit}/{filename}"
    )
    # os.remove("assets/temp/temp.mp4")

    print_step("Removing temporary files 🗑")
    cleanups = cleanup()
    print_substep(f"Removed {cleanups} temporary files 🗑")
    print_substep("See result in the results folder!")

    print_step(
        f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {os.getenv("background_credit")}'
    )
