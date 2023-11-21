import json
import random
import re
import math
from pathlib import Path
from random import randrange
from typing import Any, Tuple, Dict

# from moviepy.editor import VideoFileClip, AudioFileClip
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from utils import settings
from utils.console import print_step, print_substep
import yt_dlp
import ffmpeg

from utils.ffmpeg import ffmpeg_progress_run, get_duration


def load_background_options():
    background_options = {}
    # Load background videos
    with open("./utils/background_videos.json") as json_file:
        background_options["video"] = json.load(json_file)

    # Load background audios
    with open("./utils/background_audios.json") as json_file:
        background_options["audio"] = json.load(json_file)

    # Remove "__comment" from backgrounds
    del background_options["video"]["__comment"]
    del background_options["audio"]["__comment"]

    for name in list(background_options["video"].keys()):
        pos = background_options["video"][name][3]

        if pos != "center":
            background_options["video"][name][3] = lambda t: ("center", pos + t)

    return background_options


def get_start_and_end_times(video_length: int, length_of_clip: int) -> Tuple[int, int]:
    """Generates a random interval of time to be used as the background of the video.

    Args:
        video_length (int): Length of the video
        length_of_clip (int): Length of the video to be used as the background

    Returns:
        tuple[int,int]: Start and end time of the randomized interval
    """
    initialValue = 180
    # Issue #1649 - Ensures that will be a valid interval in the video
    while int(length_of_clip) <= int(video_length + initialValue):
        if initialValue == initialValue // 2:
            raise Exception("Your background is too short for this video length")
        else:
            initialValue //= 2  # Divides the initial value by 2 until reach 0
    random_time = randrange(initialValue, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def get_background_config(mode: str):
    """Fetch the background/s configuration"""
    try:
        choice = str(settings.config["settings"]["background"][f"background_{mode}"]).casefold()
    except AttributeError:
        print_substep("No background selected. Picking random background'")
        choice = None

    # Handle default / not supported background using default option.
    # Default : pick random from supported background.
    if not choice or choice not in background_options[mode]:
        choice = random.choice(list(background_options[mode].keys()))

    return background_options[mode][choice]


def download_background_video(background_config: Tuple[str, str, str, Any]):
    """Downloads the background/s video from YouTube."""
    Path("./assets/backgrounds/video/").mkdir(parents=True, exist_ok=True)
    # note: make sure the file name doesn't include an - in it
    uri, filename, credit, _ = background_config
    if Path(f"assets/backgrounds/video/{credit}-{filename}").is_file():
        return
    print_step(
        "We need to download the backgrounds videos. they are fairly large but it's only done once. 😎"
    )
    print_substep("Downloading the backgrounds videos... please be patient 🙏 ")
    print_substep(f"Downloading {filename} from {uri}")
    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]",
        "outtmpl": f"assets/backgrounds/video/{credit}-{filename}",
        "retries": 10,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(uri)
    print_substep("Background video downloaded successfully! 🎉", style="bold green")


def download_background_audio(background_config: Tuple[str, str, str]):
    """Downloads the background/s audio from YouTube."""
    Path("./assets/backgrounds/audio/").mkdir(parents=True, exist_ok=True)
    # note: make sure the file name doesn't include an - in it
    uri, filename, credit = background_config
    if Path(f"assets/backgrounds/audio/{credit}-{filename}").is_file():
        return
    print_step(
        "We need to download the backgrounds audio. they are fairly large but it's only done once. 😎"
    )
    print_substep("Downloading the backgrounds audio... please be patient 🙏 ")
    print_substep(f"Downloading {filename} from {uri}")
    ydl_opts = {
        "outtmpl": f"./assets/backgrounds/audio/{credit}-{filename}",
        "format": "bestaudio/best",
        "extract_audio": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([uri])

    print_substep("Background audio downloaded successfully! 🎉", style="bold green")


def chop_background(background_config: Dict[str, Tuple], video_length: int, reddit_object: dict):
    """Generates the background audio and footage to be used in the video and writes it to assets/temp/background.mp3 and assets/temp/background.mp4

    Args:
        background_config (Dict[str,Tuple]]) : Current background configuration
        video_length (int): Length of the clip where the background footage is to be taken out of
    """
    id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])

    if settings.config["settings"]["background"][f"background_audio_volume"] == 0:
        print_step("Volume was set to 0. Skipping background audio creation . . .")
    else:
        audio_choice = f"{background_config['audio'][2]}-{background_config['audio'][1]}"
        audio_file_path=f"assets/backgrounds/audio/{audio_choice}"
        audio_file_duration=get_duration(audio_file_path)
        if bool(settings.config["settings"]["background"][f"background_audio_loop"]):
            background_looped_audio_file_path = f"assets/backgrounds/audio/looped-{audio_choice}"
            background_audio_loops = math.ceil(video_length / audio_file_duration)
            if background_audio_loops > 1:
                print_step(f"Looping background audio {background_audio_loops} times...🔁")
                background_audio_loop_input = ffmpeg.input(
                    audio_file_path,
                    stream_loop=background_audio_loops
                )
                ffmpeg_progress_run(
                    ffmpeg.output(
                        background_audio_loop_input,
                        background_looped_audio_file_path,
                        vcodec="copy",
                        acodec="copy"
                    ).overwrite_output(),
                    background_audio_loops*audio_file_duration
                )
                audio_file_path = background_looped_audio_file_path
                audio_file_duration = audio_file_duration*background_audio_loops
        print_step("Finding a spot in the background audio to chop...✂️")
        start_time_audio, end_time_audio = get_start_and_end_times(
            video_length, audio_file_duration
        )
        # background_audio = background_audio.subclip(start_time_audio, end_time_audio)
        # background_audio.write_audiofile(f"assets/temp/{id}/background.mp3")
        # background_audio.close()
        ffmpeg_progress_run(
            ffmpeg.input(audio_file_path).output(
                f"assets/temp/{id}/background.mp3",
                # acodec="copy",
                # acodec="libmp3lame",
                map="0",
                ss=start_time_audio,
                to=end_time_audio
            ).overwrite_output(),
            end_time_audio-start_time_audio
        )

    video_choice = f"{background_config['video'][2]}-{background_config['video'][1]}"
    video_file_path = f"assets/backgrounds/video/{video_choice}"
    video_file_duration=get_duration(video_file_path)
    # print(f"Original duration before looping: {video_file_duration}")
    if bool(settings.config["settings"]["background"][f"background_video_loop"]):
        background_looped_video_file_path = f"assets/backgrounds/video/looped-{video_choice}"
        background_video_loops = math.ceil(video_length / video_file_duration)
        if background_video_loops > 1:
            print_step(f"Looping background video {background_video_loops} times...🔁")
            background_video_loop_input = ffmpeg.input(
                video_file_path,
                stream_loop=background_video_loops
            )
            ffmpeg_progress_run(
                ffmpeg.output(
                    background_video_loop_input,
                    background_looped_video_file_path,
                    vcodec="copy",
                    acodec="copy"
                ).overwrite_output(),
                background_video_loops*video_file_duration
            )
            video_file_path = background_looped_video_file_path
            video_file_duration = video_file_duration * background_video_loops

    # print(f"Calculated duration after looping: {video_file_duration}")
    # print(f"Actual duration after looping: {get_duration(video_file_path)}")
    print_step("Finding a spot in the background video to chop...✂️")
    start_time_video, end_time_video = get_start_and_end_times(
        video_length, video_file_duration
    )
    # Extract video subclip
    # try:
    ffmpeg_progress_run(
        ffmpeg.input(video_file_path, ss=("%0.2f" % start_time_video), t=("%0.2f" % (end_time_video-start_time_video))).output(f"assets/temp/{id}/background.mp4", vcodec="copy", acodec="copy", map="0"),
        end_time_video-start_time_video
    )
        # ffmpeg_extract_subclip(
        #     video_file_path,
        #     start_time_video, # -ss
        #     end_time_video, # -to
        #     targetname=f"assets/temp/{id}/background.mp4",
        # )
    # except (OSError, IOError):  # ffmpeg issue see #348
    #     print_substep("FFMPEG issue. Trying again...")
    #     video=VideoFileClip(video_file_path)
    #     new = video.subclip(start_time_video, end_time_video)
    #     new.write_videofile(f"assets/temp/{id}/background.mp4")
    #     video.close()
    print_substep("Background video chopped successfully!", style="bold green")
    return background_config["video"][2]


# Create a tuple for downloads background (background_audio_options, background_video_options)
background_options = load_background_options()
