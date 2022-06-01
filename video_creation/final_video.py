import json
import os
import time
from os.path import exists

from moviepy.editor import (VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips, concatenate_audioclips,
                            CompositeAudioClip, CompositeVideoClip)

from utils.cleanup import cleanup
from utils.console import print_step, print_substep

W, H = 1080, 1920


def make_final_video(number_of_clips):
    print_step("Creating the final video 🎥")
    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    background_clip = (
        VideoFileClip("assets/temp/backgrounds.mp4").without_audio().resize(height=H).crop(x1=1166.6, y1=0, x2=2246.6,
                                                                                           y2=1920))
    # Gather all audio clips
    audio_clips = []
    for i in range(0, number_of_clips):
        audio_clips.append(AudioFileClip(f"assets/temp/mp3/{i}.mp3"))
    audio_clips.insert(0, AudioFileClip(f"assets/temp/mp3/title.mp3"))
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])

    # Gather all images
    image_clips = []
    for i in range(0, number_of_clips):
        image_clips.append(
            ImageClip(f"assets/temp/png/comment_{i}.png").set_duration(audio_clips[i + 1].duration).set_position(
                "center").resize(width=W - 100), )
    image_clips.insert(0, ImageClip(f"assets/temp/png/title.png").set_duration(audio_clips[0].duration).set_position(
        "center").resize(width=W - 100), )
    image_concat = concatenate_videoclips(image_clips).set_position(("center", "center"))
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])

    def get_video_title() -> str:
        title = os.getenv("VIDEO_TITLE") or "final_video"
        if len(title) <= 35:
            return title
        else:
            return title[0:30] + "..."

    filename = f'{get_video_title()}.mp4'

    def save_data():
        with open('./video_creation/data/videos.json', 'r+') as raw_vids:
            done_vids = json.load(raw_vids)
            if str(os.getenv("VIDEO_ID")) in [video['id'] for video in done_vids]:
                return  # video already done but was specified to continue anyway in the .env file
            payload = {"id": str(os.getenv("VIDEO_ID")), 'time': str(int(time.time())),
                       "background_credit": str(os.getenv('background_credit')),
                       "reddit_title": str(os.getenv('VIDEO_TITLE')), "filename": filename}
            done_vids.append(payload)
            raw_vids.seek(0)
            json.dump(done_vids, raw_vids, ensure_ascii=False, indent=4)

    save_data()
    if not exists('./results'):
        print_substep('the results folder didn\'t exist so I made it')
        os.mkdir("./results")
    final.write_videofile(f"results/{filename}", fps=30, audio_codec="aac", audio_bitrate="192k")
    print_step("Removing temporary files 🗑")
    cleanups = cleanup()
    print_substep(f"Removed {cleanups} temporary files 🗑")
    print_substep(f"See result in the results folder!")

    print_step(f"Reddit title: {os.getenv('VIDEO_TITLE')} \n Background Credit: {os.getenv('background_credit')}")
