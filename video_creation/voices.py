#!/usr/bin/env python3
from os import getenv
from pathlib import Path

import sox
from mutagen import MutagenError
from mutagen.mp3 import MP3, HeaderNotFoundError
from rich.console import Console
from rich.progress import track

from TTS.swapper import TTS

from utils.console import print_step, print_substep
from utils.voice import sanitize_text

console = Console()


VIDEO_LENGTH: int = 40  # secs


def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.
    Args:
            reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/temp/mp3").mkdir(parents=True, exist_ok=True)
    TextToSpeech = TTS()
    TextToSpeech.tts(
        sanitize_text(reddit_obj["thread_title"]),
        filename="assets/temp/mp3/title.mp3",
        random_speaker=False,
    )
    try:
        length += MP3("assets/temp/mp3/title.mp3").info.length
    except HeaderNotFoundError:  # note to self AudioFileClip
        length += sox.file_info.duration("assets/temp/mp3/title.mp3")
    if getenv("STORYMODE").casefold() == "true":
        TextToSpeech.tts(
            sanitize_text(reddit_obj["thread_content"]),
            filename="assets/temp/mp3/story_content.mp3",
            random_speaker=False,
        )
        # 'story_content'
    com = 0
    for comment in track((reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than VIDEO_LENGTH seconds. This can be longer
        # but this is just a good_voices starting point
        if length > VIDEO_LENGTH:
            break

        TextToSpeech.tts(
            sanitize_text(comment["comment_body"]),
            filename=f"assets/temp/mp3/{com}.mp3",
            random_speaker=False,
        )
        try:
            length += MP3(f"assets/temp/mp3/{com}.mp3").info.length
            com += 1
        except (HeaderNotFoundError, MutagenError, Exception):
            try:
                length += sox.file_info.duration(f"assets/temp/mp3/{com}.mp3")
                com += 1
            except (OSError, IOError):
                print(
                    "would have removed"
                    f"assets/temp/mp3/{com}.mp3"
                    f"assets/temp/png/comment_{com}.png"
                )
                # remove(f"assets/temp/mp3/{com}.mp3")
                # remove(f"assets/temp/png/comment_{com}.png")# todo might cause odd un-syncing

    print_substep("Saved Text to MP3 files Successfully.", style="bold green")
    # ! Return the index, so we know how many screenshots of comments we need to make.
    return length, com
