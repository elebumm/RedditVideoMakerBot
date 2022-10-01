import multiprocessing
import os
import re
from os.path import exists
from typing import Tuple, Any, Final

from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from rich.console import Console

from utils import settings
from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.video import Video
from utils.videos import save_data

console = Console()


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


def prepare_background(id: str, W: int, H: int) -> VideoFileClip:
    clip = (
        VideoFileClip(f"assets/temp/{id}/background.mp4")
        .without_audio()
        .resize(height=H)
    )

    # calculate the center of the background clip
    c = clip.w // 2

    # calculate the coordinates where to crop
    half_w = W // 2
    x1 = c - half_w
    x2 = c + half_w

    return clip.crop(x1=x1, y1=0, x2=x2, y2=H)


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
    # settings values
    W: Final[int] = int(settings.config["settings"]["resolution_w"])
    H: Final[int] = int(settings.config["settings"]["resolution_h"])

    # try:  # if it isn't found (i.e you just updated and copied over config.toml) it will throw an error
    #    VOLUME_MULTIPLIER = settings.config["settings"]['background']["background_audio_volume"]
    # except (TypeError, KeyError):
    #    print('No background audio volume found in config.toml. Using default value of 1.')
    #    VOLUME_MULTIPLIER = 1

    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    print_step("Creating the final video 🎥")

    VideoFileClip.reW = lambda clip: clip.resize(width=W)
    VideoFileClip.reH = lambda clip: clip.resize(width=H)

    opacity = settings.config["settings"]["opacity"]
    transition = settings.config["settings"]["transition"]

    background_clip = prepare_background(id, W=W, H=H)

    # Gather all audio clips
    audio_clips = [
        AudioFileClip(f"assets/temp/{id}/mp3/{i}.mp3") for i in range(number_of_clips)
    ]
    audio_clips.insert(0, AudioFileClip(f"assets/temp/{id}/mp3/title.mp3"))
    audio_concat = concatenate_audioclips(audio_clips)
    audio_composite = CompositeAudioClip([audio_concat])

    console.log(f"[bold green] Video Will Be: {length} Seconds Long")
    # add title to video
    image_clips = []
    # Gather all images
    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)
    new_transition = (
        0 if transition is None or float(transition) > 2 else float(transition)
    )
    screenshow_width = int((W * 90) // 100)
    image_clips.insert(
        0,
        ImageClip(f"assets/temp/{id}/png/title.png")
        .set_duration(audio_clips[0].duration)
        .resize(width=screenshow_width)
        .set_opacity(new_opacity)
        .crossfadein(new_transition)
        .crossfadeout(new_transition),
    )

    for i in range(0, number_of_clips):
        image_clips.append(
            ImageClip(f"assets/temp/{id}/png/comment_{i}.png")
            .set_duration(audio_clips[i + 1].duration)
            .resize(width=screenshow_width)
            .set_opacity(new_opacity)
            .crossfadein(new_transition)
            .crossfadeout(new_transition)
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
    image_concat = concatenate_videoclips(image_clips).set_position(
        img_clip_pos
    )  # note transition kwarg for delay in imgs
    image_concat.audio = audio_composite
    final = CompositeVideoClip([background_clip, image_concat])
    title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])
    idx = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    filename = f"{name_normalize(title)[:251]}.mp4"
    subreddit = settings.config["reddit"]["thread"]["subreddit"]

    if not exists(f"./results/{subreddit}"):
        print_substep("The results folder didn't exist so I made it")
        os.makedirs(f"./results/{subreddit}")

    # if settings.config["settings"]['background']["background_audio"] and exists(f"assets/backgrounds/background.mp3"):
    #    audioclip = mpe.AudioFileClip(f"assets/backgrounds/background.mp3").set_duration(final.duration)
    #    audioclip = audioclip.fx( volumex, 0.2)
    #    final_audio = mpe.CompositeAudioClip([final.audio, audioclip])
    #    # lowered_audio = audio_background.multiply_volume( # todo get this to work
    #    #    VOLUME_MULTIPLIER)  # lower volume by background_audio_volume, use with fx
    #    final.set_audio(final_audio)

    final = Video(final).add_watermark(
        text=f"Background credit: {background_config[2]}",
        opacity=0.4,
        redditid=reddit_obj,
    )
    final.write_videofile(
        f"assets/temp/{id}/temp.mp4",
        fps=30,
        audio_codec="aac",
        audio_bitrate="192k",
        verbose=False,
        threads=multiprocessing.cpu_count(),
    )
    ffmpeg_extract_subclip(
        f"assets/temp/{id}/temp.mp4",
        0,
        length,
        targetname=f"results/{subreddit}/{filename}",
    )
    save_data(subreddit, filename, title, idx, background_config[2])
    print_step("Removing temporary files 🗑")
    cleanups = cleanup(id)
    print_substep(f"Removed {cleanups} temporary files 🗑")
    print_substep("See result in the results folder!")

    print_step(
        f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {background_config[2]}'
    )
