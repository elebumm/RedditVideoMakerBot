from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track

import os

def total_length(largest_file_index):
    length = MP3(f"assets/mp3/title.mp3").info.length
    for index in range(largest_file_index + 1):
        length += MP3(f"assets/mp3/{index}.mp3").info.length
    return length

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    total_files = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    tts = gTTS(text=reddit_obj["thread_title"], tld=os.getenv("ACCENT"), slow=False)
    tts.save(f"assets/mp3/title.mp3")

    for i, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        tts = gTTS(text=comment["comment_body"], tld=os.getenv("ACCENT"), slow=False)
        tts.save(f"assets/mp3/{total_files}.mp3")
        if total_length(total_files) < 60:
            total_files += 1
        else:
            break

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return total_length(total_files - 1), total_files
