import os
import re

from dotenv import load_dotenv
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
    CompositeVideoClip,
)

import reddit.subreddit
from utils.console import print_step, print_substep


def make_final_video(number_of_clips, file_name):
    load_dotenv()
    opacity = os.getenv("OPACITY")

    print_step("Creating the final video...")

    VideoFileClip.reW = lambda clip: clip.resize(width=1080)
    VideoFileClip.reH = lambda clip: clip.resize(width=1920)

    background_clip = (
        VideoFileClip("assets/mp4/clip.mp4")
        .without_audio()
        .resize(height=1920)
        .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )

    try:
        opacity = float(os.getenv("OPACITY"))
    except (
            ValueError,
            FloatingPointError,
            TypeError
        ):
        print_substep(
            "Please ensure that OPACITY is between 0 and 1 in .env file", style_="bold red"
        )

    # Gather all audio clips
    audio_clips = []
    for i in range(0, number_of_clips):
        audio_clips.append(AudioFileClip(f"assets/mp3/{i}.mp3"))

    audio_clips.insert(0, AudioFileClip("assets/mp3/title.mp3"))
    try:
        audio_clips.insert(1, AudioFileClip("assets/mp3/posttext.mp3"))
    except (
            OSError,
            FileNotFoundError,
        ):
        print_substep("An error occured! Aborting.", style_="bold red")
        raise SystemExit()
    else:
        audio_concat = concatenate_audioclips(audio_clips)
        audio_composite = CompositeAudioClip([audio_concat])


    # Gather all images
    image_clips = []
    for i in range(0, number_of_clips):
        image_clips.append(
            ImageClip(f"assets/png/comment_{i}.png")
            .set_duration(audio_clips[i + 1].duration)
            .set_position("center")
            .resize(width=1080 - 100)
            .set_opacity(float(opacity)),
        )


    image_concat = concatenate_videoclips(image_clips).set_position(("center", "center"))
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])

    if file_name is None:
        filename =  re.sub(
            "[?\"%*:|<>]/", "", (f"assets/{reddit.subreddit.submission.title}.mp4")
        )

    final.write_videofile(filename, fps=30, audio_codec="aac", audio_bitrate="192k")
