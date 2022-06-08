#!/usr/bin/env python3
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
import re
from utils.console import print_step, print_substep
from dotenv import load_dotenv
import os

W, H = 1080, 1920


def name_normalize(
        name: str
) -> str:
    name = re.sub(r'[?\\"%*:|<>]', '', name)
    name = re.sub(r'(\D+)/(\D+)', r'\1\ or\ \2', name)
    name = re.sub(r'(\d+)/(\d+)', r'\1\ of\ \2', name)
    return name


def make_final_video(number_of_clips):

    # Calls opacity from the .env
    load_dotenv()
    opacity = os.getenv("OPACITY")

    print_step("Creating the final video...")

    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    background_clip = (
        VideoFileClip("assets/mp4/clip.mp4")
        .without_audio()
        .resize(height=H)
        .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )

    # Gather all audio clips
    audio_clips = []
    for i in range(0, number_of_clips):
        audio_clips.append(AudioFileClip(f"assets/mp3/{i}.mp3"))
    audio_clips.insert(0, AudioFileClip("assets/mp3/title.mp3"))
    try:
        audio_clips.insert(1, AudioFileClip("assets/mp3/posttext.mp3"))
    except:
        OSError()
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])

    # Gather all images
    image_clips = []
    for i in range(0, number_of_clips):
        image_clips.append(
            ImageClip(f"assets/png/comment_{i}.png")
            .set_duration(audio_clips[i + 1].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
        )
    if os.path.exists("assets/mp3/posttext.mp3"):
        image_clips.insert(
            0,
            ImageClip("assets/png/title.png")
            .set_duration(audio_clips[0].duration + audio_clips[1].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
        )
    else:
        image_clips.insert(
            0,
            ImageClip("assets/png/title.png")
            .set_duration(audio_clips[0].duration)
            .set_position("center")
            .resize(width=W - 100)
            .set_opacity(float(opacity)),
        )
    image_concat = concatenate_videoclips(image_clips).set_position(
        ("center", "center")
    )
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])
    final_video_path = "assets/"
    if os.getenv("FINAL_VIDEO_PATH"):
        final_video_path = os.getenv("FINAL_VIDEO_PATH")
        filename = final_video_path + name_normalize(reddit.subreddit.submission.title) + ".mp4"
    try:
        final.write_videofile(filename, fps=30, audio_codec="aac", audio_bitrate="192k")
    except:
        print_substep("Something's wrong with the path you inserted, the video will be saved in the default path (assets/)", style="bold red")
        filename = (re.sub('[?\"%*:|<>]', '', ("assets/" + reddit.subreddit.submission.title + ".mp4")))
        final.write_videofile(filename, fps=30, audio_codec="aac", audio_bitrate="192k")
    for i in range(0, number_of_clips):
        pass
