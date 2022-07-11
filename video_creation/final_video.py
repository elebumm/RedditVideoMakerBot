#!/usr/bin/env python3
import multiprocessing
import os
import re
from os.path import exists
from typing import Tuple, Any

import translators as ts

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeVideoClip,
)
from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio, ffmpeg_extract_subclip
from rich.console import Console

from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.videos import save_data
from utils import settings
from video_creation.background import download_background, chop_background_video

console = Console()

W, H = 1080, 1920  # TODO move to config


def name_normalize(
        name: str
) -> str:
    name = re.sub(r'[?\\"%*:|<>]', "", name)
    name = re.sub(r'( [w,W]\s?\/\s?[o,O,0])', r' without', name)
    name = re.sub(r'( [w,W]\s?\/)', r' with', name)
    name = re.sub(r'(\d+)\s?\/\s?(\d+)', r'\1 of \2', name)
    name = re.sub(r'(\w+)\s?\/\s?(\w+)', r'\1 or \2', name)
    name = re.sub(r'\/', '', name)

    lang = settings.config['reddit']['thread']['post_lang']
    if lang:
        print_substep('Translating filename...')
        translated_name = ts.google(name, to_language=lang)
        return translated_name

    else:
        return name


def make_final_video(
        indexes_of_clips: list,
        reddit_obj: dict,
        background_config: Tuple[str, str, str, Any],
) -> None:
    """
    Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp

    Args:
        indexes_of_clips (list): Indexes with created comments'
        reddit_obj (dict): The reddit object that contains the posts to read.
        background_config (Tuple[str, str, str, Any]): The background config to use.
    """
    print_step('Creating the final video 🎥')
    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)
    opacity = settings.config['settings']['opacity']

    final_length = 0

    # Gather all audio clips
    audio_clips = [AudioFileClip(f'assets/temp/mp3/{i}.mp3') for i in indexes_of_clips]
    audio_clips.insert(0, AudioFileClip('assets/temp/mp3/title.mp3'))
    audio_composite = concatenate_audioclips(audio_clips)

    console.log(f'[bold green] Video Will Be: {audio_composite.length} Seconds Long')
    # add title to video
    image_clips = []
    # Gather all images
    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)
    image_clips.insert(
        0,
        ImageClip('assets/temp/png/title.png')
        .set_duration(audio_clips[0].duration)
        .resize(width=W - 100)
        .set_opacity(new_opacity),
    )

    for i in indexes_of_clips:
        image_clips.append(
            ImageClip(f'assets/temp/png/comment_{i}.png')
            .set_duration(audio_clips[i + 1].duration)
            .resize(width=W - 100)
            .set_opacity(new_opacity)
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
    # else: story mode stuff
    img_clip_pos = background_config[3]
    image_concat = concatenate_videoclips(image_clips).set_position(img_clip_pos)
    image_concat.audio = audio_composite

    download_background(background_config)
    chop_background_video(background_config, final_length)
    background_clip = (
        VideoFileClip("assets/temp/background.mp4")
        .without_audio()
        .resize(height=H)
        .crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
    )

    final = CompositeVideoClip([background_clip, image_concat])
    title = re.sub(r'[^\w\s-]', '', reddit_obj['thread_title'])
    idx = re.sub(r'[^\w\s-]', '', reddit_obj['thread_id'])

    filename = f'{name_normalize(title)}.mp4'
    subreddit = settings.config['reddit']['thread']['subreddit']

    save_data(subreddit, filename, title, idx, background_config[2])

    if not exists(f'./results/{subreddit}'):
        print_substep('The results folder didn\'t exist so I made it')
        os.makedirs(f'./results/{subreddit}')

    final.write_videofile(
        'assets/temp/temp.mp4',
        fps=30,
        audio_codec='aac',
        audio_bitrate='192k',
        verbose=False,
        threads=multiprocessing.cpu_count(),
    )
    if settings.config['settings']['background_audio']:
        print('[bold green] Merging background audio with video')
        if not exists('assets/backgrounds/background.mp3'):
            print_substep(
                'Cannot find assets/backgrounds/background.mp3 audio file didn\'t so skipping.'
            )
            ffmpeg_extract_subclip(
                'assets/temp/temp.mp4',
                0,
                final.duration,
                targetname=f'results/{subreddit}/{filename}',
            )
        else:
            ffmpeg_merge_video_audio(
                'assets/temp/temp.mp4',
                'assets/backgrounds/background.mp3',
                'assets/temp/temp_audio.mp4',
            )
            ffmpeg_extract_subclip(  # check if this gets run
                'assets/temp/temp_audio.mp4',
                0,
                final.duration,
                targetname=f"results/{subreddit}/{filename}",
            )
    else:
        print('debug duck')
        ffmpeg_extract_subclip(
            'assets/temp/temp.mp4',
            0,
            final.duration,
            targetname=f'results/{subreddit}/{filename}',
        )
    print_step('Removing temporary files 🗑')
    cleanups = cleanup()
    print_substep(f'Removed {cleanups} temporary files 🗑')
    print_substep('See result in the results folder!')

    print_step(
        f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {background_config[2]}'
    )
