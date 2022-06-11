#!/usr/bin/env python3
from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track
from rich.console import Console
import re

from video_creation.profane_list.en import profane_list

console = Console()


def profane_filter(text: str, word_list: list) -> str:
    word_list.sort(reverse=True, key=len)
    filtered_text = text
    if any([word in word_list for word in text.split()]):
        for word in word_list:
            if word in text:
                word_lenght = word.__len__()
                word_half = word_lenght // 2 if word_lenght % 2 == 0 else word_lenght // 2 + 1
                filtered_text = re.sub(word, f'{word[:word_half]}{(word_lenght - word_half) * "*"}', filtered_text)
    return filtered_text


def save_text_to_mp3(reddit_obj: dict) -> tuple:
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    tts = gTTS(text=profane_filter(reddit_obj["thread_title"], profane_list), lang="en", slow=False)
    tts.save("assets/mp3/title.mp3")
    length += MP3("assets/mp3/title.mp3").info.length

    try:
        Path("assets/mp3/posttext.mp3").unlink()
    except OSError:
        pass

    if reddit_obj["thread_post"] != "":
        tts = gTTS(text=reddit_obj["thread_post"], lang="en", slow=False)
        tts.save("assets/mp3/posttext.mp3")
        length += MP3("assets/mp3/posttext.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"])):

        # Allow user to see what comment is being saved
        print_substep(f"Saving MP3 {idx + 1} ")

        # Stop creating mp3 files if the length is greater than 50 seconds.
        # This can be longer, but this is just a good starting point
        if length > 50:
            break
        comment = comment["comment_body"]
        text = re.sub('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*',
                      '', comment)
        text = profane_filter(text, profane_list)
        tts = gTTS(text, lang="en", slow=False)
        tts.save(f"assets/mp3/{idx}.mp3")
        length += MP3(f"assets/mp3/{idx}.mp3").info.length

    # Let user know that the MP3 files are saved
    console.log(f"[bold green]Saved {idx + 1} MP3 Files.")
    # Return the index, so we know how many screenshots of comments we need to make.
    return length, idx
