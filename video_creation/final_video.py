from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeAudioClip,
    CompositeVideoClip,
)
from utils.console import print_step
import re
from pathlib import Path

import subprocess
from typing import List

W, H = 1080, 1920


def make_final_video(number_of_clips, chosen_subreddit, video_title, ffmpeg_exe, video_speed):
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
    audio_clips.insert(0, AudioFileClip(f"assets/mp3/title.mp3"))
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])

    # Gather all images
    image_clips = []
    for i in range(0, number_of_clips):
        image_clips.append(
            ImageClip(f"assets/png/comment_{i}.png")
            .set_duration(audio_clips[i + 1].duration)
            .set_position("center")
            .resize(width=W - 100),
        )
    image_clips.insert(
        0,
        ImageClip(f"assets/png/title.png")
        .set_duration(audio_clips[0].duration)
        .set_position("center")
        .resize(width=W - 100),
    )
    image_concat = concatenate_videoclips(image_clips).set_position(
        ("center", "center")
    )
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])
    final.write_videofile(
        "assets/final_video_raw.mp4", fps=30, audio_codec="aac", audio_bitrate="192k"
    )

    videos = [
        Video(speed=video_speed, path="assets/final_video_raw.mp4"),
    ]

    print_step("Creating sped up version of the final video...")

    Path("final/").mkdir(parents=True, exist_ok=True)
    final_video_title = urlify(chosen_subreddit)+"-"+urlify(video_title)+".mp4"
    concatenate_videos(ffmpeg_exe,
        videos=videos, output_file=f"final/"+final_video_title)
    for i in range(0, number_of_clips):
        pass


class Video():
    def __init__(self, path: str, speed: float = 1.0):
        self.path = path
        self.speed = speed


def concatenate_videos(ffmpeg_exe, videos: List[Video], output_file: str):

    COMMAND_BASE = [ffmpeg_exe]
    COMMAND_BASE += ["-n"]  # disable file overwriting

    video_count = len(videos)
    video_speeds = [float(1/x.speed) for x in videos]
    audio_speeds = [float(x.speed) for x in videos]

    cmd_input_files = []
    filters, concat = ("", "")
    for i, x in enumerate(videos):
        cmd_input_files += ["-i", x.path]
        filters += f"[{i}:v] setpts = {video_speeds[i]} * PTS [v{i}];"
        filters += f"[{i}:a] atempo = {audio_speeds[i]}       [a{i}];"
        concat += f"[v{i}][a{i}]"
    concat += f"concat = n = {video_count}:v = 1:a = 1 [v_all][a_all]"

    filter_complex = f"{filters}{concat}".replace(" ", "")

    cmd_filter_complex = [
        "-filter_complex", filter_complex,
    ]
    cmd_map = [
        "-map", "[v_all]",
        "-map", "[a_all]",
    ]
    command = sum([
        COMMAND_BASE,
        cmd_input_files,
        cmd_filter_complex,
        cmd_map,
        [output_file],
    ], [])

    subprocess.run(command)


def urlify(s):

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '-', s)

    return s
