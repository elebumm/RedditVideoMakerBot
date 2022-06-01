import sox
from pathlib import Path

from mutagen import MutagenError
from mutagen.mp3 import MP3, HeaderNotFoundError
from utils.console import print_step, print_substep
from rich.progress import track

from video_creation.TTSwrapper import TTTTSWrapper


def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files 🎶")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/temp/mp3").mkdir(parents=True, exist_ok=True)

    ttttsw = TTTTSWrapper()  # tiktok text to speech wrapper
    ttttsw.tts(reddit_obj["thread_title"], filename=f"assets/temp/mp3/title.mp3", random_speaker=True)
    try:
        length += MP3(f"assets/temp/mp3/title.mp3").info.length
    except HeaderNotFoundError:
        length = sox.file_info.duration(f"assets/temp/mp3/title.mp3")

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good_voices starting point
        if length > 50:
            break

        ttttsw.tts(comment["comment_body"], filename=f"assets/temp/mp3/{idx}.mp3", random_speaker=False)
        try:
            length += MP3(f"assets/temp/mp3/{idx}.mp3").info.length
        except HeaderNotFoundError or MutagenError:
            length = sox.file_info.duration(f"assets/temp/mp3/{idx}.mp3")

    print_substep("Saved Text to MP3 files Successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
