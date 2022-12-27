import os
import re
import multiprocessing
from os.path import exists
from typing import Tuple, Any, Final
import translators as ts
import shutil
from typing import Tuple, Any
from PIL import Image

from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from rich.console import Console
from rich.progress import track

import ffmpeg

from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.video import Video
from utils.videos import save_data
from utils.thumbnail import create_thumbnail
from utils import settings
from utils.thumbnail import create_thumbnail

console = Console()


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


def prepare_background(reddit_id: str, W: int, H: int) -> str:
    output_path = f"assets/temp/{reddit_id}/background_noaudio.mp4"
    if settings.config["settings"]["storymode"]:
        output = ffmpeg.input(f"assets/temp/{reddit_id}/background.mp4").output(output_path, an=None, **{"c:v": "h264"}).overwrite_output()
    else:
        output = ffmpeg.input(f"assets/temp/{reddit_id}/background.mp4").filter('crop', "ih*(9/16)", "ih").output(output_path, an=None, **{"c:v": "h264"}).overwrite_output()
    output.run()
    return output_path


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

    reddit_id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    print_step("Creating the final video 🎥")

    opacity = settings.config["settings"]["opacity"]
    transition = settings.config["settings"]["transition"]

    background_clip = ffmpeg.input(prepare_background(reddit_id, W=W, H=H))

    # Gather all audio clips
    audio_clips = list()
    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 0:
            audio_clips = [ffmpeg.input(f"assets/temp/{reddit_id}/mp3/title.mp3")]
            audio_clips.insert(1, ffmpeg.input(f"assets/temp/{reddit_id}/mp3/postaudio.mp3"))
        elif settings.config["settings"]["storymodemethod"] == 1:
            audio_clips = [
                ffmpeg.input(f"assets/temp/{reddit_id}/mp3/postaudio-{i}.mp3")
                for i in track(
                    range(number_of_clips + 1), "Collecting the audio files..."
                )
            ]
            audio_clips.insert(0, ffmpeg.input(f"assets/temp/{reddit_id}/mp3/title.mp3"))

    else:
        audio_clips = [ffmpeg.input(f"assets/temp/{reddit_id}/mp3/{i}.mp3") for i in range(number_of_clips)]
        audio_clips.insert(0, ffmpeg.input(f"assets/temp/{reddit_id}/mp3/title.mp3"))
        
    audio_clips_durations = [float(ffmpeg.probe(f"assets/temp/{reddit_id}/mp3/{i}.mp3")['format']['duration']) for i in range(number_of_clips)]
    audio_clips_durations.insert(0, float(ffmpeg.probe(f"assets/temp/{reddit_id}/mp3/title.mp3")['format']['duration']))
    audio_concat = ffmpeg.concat(*audio_clips, a=1, v=0)
    ffmpeg.output(audio_concat, f"assets/temp/{reddit_id}/audio.mp3").overwrite_output().run()

    console.log(f"[bold green] Video Will Be: {length} Seconds Long")
    # Gather all images
    new_opacity = 1 if opacity is None or float(opacity) >= 1 else float(opacity)
    new_transition = (
        0 if transition is None or float(transition) > 2 else float(transition)
    )
    screenshot_width = "iw-800"

    audio = ffmpeg.input(f"assets/temp/{reddit_id}/audio.mp3")
    video = ffmpeg.input(f"assets/temp/{reddit_id}/background_noaudio.mp4")

    image_clips = list()

    image_clips.insert(
        0,
        ffmpeg.input(f"assets/temp/{reddit_id}/png/title.png")['v']
        .filter('scale', screenshot_width, -1)
    )

    current_time = 0
    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 0:
            image_clips.insert(
                1,
                ffmpeg.input(f"assets/temp/{reddit_id}/png/story_content.png")
                .filter('scale', screenshot_width, -1)
            )
            video = video.overlay(image_clips[i], enable=f'between(t,{current_time},{current_time + audio_clips_durations[i]})', x='(main_w-overlay_w)/2', y='(main_h-overlay_h)/2')
            current_time += audio_clips_durations[i]
        elif settings.config["settings"]["storymodemethod"] == 1:
            for i in track(
                range(0, number_of_clips + 1), "Collecting the image files..."
            ):
                image_clips.append(
                    ffmpeg.input(f"assets/temp/{reddit_id}/png/img{i}.png")['v']
                    .filter('scale', screenshot_width, -1)
                )
                video = video.overlay(image_clips[i], enable=f'between(t,{current_time},{current_time + audio_clips_durations[i]})', x='(main_w-overlay_w)/2', y='(main_h-overlay_h)/2')
                current_time += audio_clips_durations[i]
    else:
        for i in range(0, number_of_clips + 1):
            image_clips.append(
                    ffmpeg.input(f"assets/temp/{reddit_id}/png/comment_{i}.png")['v']
                    .filter('scale', screenshot_width, -1)
            )
            video = video.overlay(image_clips[i], enable=f'between(t,{current_time},{current_time + audio_clips_durations[i]})', x='(main_w-overlay_w)/2', y='(main_h-overlay_h)/2')
            current_time += audio_clips_durations[i]

    title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])
    idx = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    title_thumb = reddit_obj["thread_title"]

    filename = f"{name_normalize(title)[:251]}"
    subreddit = settings.config["reddit"]["thread"]["subreddit"]

    final = ffmpeg.output(video, audio, f"results/{subreddit}/{filename}.mp4", f='mp4', **{"c:v": "h264"}).overwrite_output()

    if not exists(f"./results/{subreddit}"):
        print_substep("The results folder didn't exist so I made it")
        os.makedirs(f"./results/{subreddit}")

    # create a tumbnail for the video
    settingsbackground = settings.config["settings"]["background"]

    if settingsbackground["background_thumbnail"]:
        if not exists(f"./results/{subreddit}/thumbnails"):
            print_substep(
                "The results/thumbnails folder didn't exist so I made it")
            os.makedirs(f"./results/{subreddit}/thumbnails")
        # get the first file with the .png extension from assets/backgrounds and use it as a background for the thumbnail
        first_image = next(
            (
                file
                for file in os.listdir("assets/backgrounds")
                if file.endswith(".png")
            ),
            None,
        )
        if first_image is None:
            print_substep("No png files found in assets/backgrounds", "red")

    if settingsbackground["background_thumbnail"] and first_image:
        font_family = settingsbackground["background_thumbnail_font_family"]
        font_size = settingsbackground["background_thumbnail_font_size"]
        font_color = settingsbackground["background_thumbnail_font_color"]
        thumbnail = Image.open(f"assets/backgrounds/{first_image}")
        width, height = thumbnail.size
        thumbnailSave = create_thumbnail(thumbnail, font_family, font_size, font_color, width, height, title_thumb)
        thumbnailSave.save(f"./assets/temp/{reddit_id}/thumbnail.png")
        print_substep(f"Thumbnail - Building Thumbnail in assets/temp/{reddit_id}/thumbnail.png")

    # create a tumbnail for the video
    settingsbackground = settings.config["settings"]["background"]

    if settingsbackground["background_thumbnail"]:
        if not exists(f"./results/{subreddit}/thumbnails"):
            print_substep(
                "The results/thumbnails folder didn't exist so I made it")
            os.makedirs(f"./results/{subreddit}/thumbnails")
        # get the first file with the .png extension from assets/backgrounds and use it as a background for the thumbnail
        first_image = next(
            (
                file
                for file in os.listdir("assets/backgrounds")
                if file.endswith(".png")
            ),
            None,
        )
        if first_image is None:
            print_substep("No png files found in assets/backgrounds", "red")

    if settingsbackground["background_thumbnail"] and first_image:
        font_family = settingsbackground["background_thumbnail_font_family"]
        font_size = settingsbackground["background_thumbnail_font_size"]
        font_color = settingsbackground["background_thumbnail_font_color"]
        thumbnail = Image.open(f"assets/backgrounds/{first_image}")
        width, height = thumbnail.size
        thumbnailSave = create_thumbnail(thumbnail, font_family, font_size, font_color, width, height, title_thumb)
        thumbnailSave.save(f"./assets/temp/{reddit_id}/thumbnail.png")
        print_substep(f"Thumbnail - Building Thumbnail in assets/temp/{reddit_id}/thumbnail.png")

    final.run()
    #get the thumbnail image from assets/temp/id/thumbnail.png and save it in results/subreddit/thumbnails
    if settingsbackground["background_thumbnail"] and exists(f"assets/temp/{reddit_id}/thumbnail.png"):
        shutil.move(f"assets/temp/{reddit_id}/thumbnail.png", f"./results/{subreddit}/thumbnails/{filename}.png")

    save_data(subreddit, filename+".mp4", title, idx, background_config[2])
    print_step("Removing temporary files 🗑")
    cleanups = cleanup(reddit_id)
    print_substep(f"Removed {cleanups} temporary files 🗑")
    print_substep("See result in the results folder!")

    print_step(
        f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {background_config[2]}'
    )
