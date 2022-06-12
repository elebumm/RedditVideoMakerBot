from pathlib import Path
from utils.console import print_step, print_substep
from rich.progress import track
from dotenv import load_dotenv
import os
from mutagen.mp3 import MP3
from video_creation.TTSwrapper import TTTTSWrapper as TTS
from rich.console import Console
console = Console()
import re

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # load_dotenv
    load_dotenv()
    Voice = os.getenv('Voice')

    # Set the voice depending on what was set in .env
    if Voice == '':
        Voice = 'en_us_002'

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    TTS.tts(str(reddit_obj["thread_title"]), "./assets/mp3/title.mp3", Voice)
    length += MP3(f"./assets/mp3/title.mp3").info.length

    try:
        Path("assets/mp3/posttext.mp3").unlink()
    except OSError:
        pass

    if reddit_obj["thread_post"] != "":
        TTS.tts(reddit_obj["thread_post"], f"assets/mp3/posttext.mp3", Voice)
        length += MP3(f"assets/mp3/posttext.mp3").info.length

    try:
        Path(f"assets/mp3/posttext.mp3").unlink()
    except OSError as e:
        pass

    if reddit_obj["thread_post"] != "":
        TTS.tts(reddit_obj["thread_post"], f"assets/mp3/posttext.mp3", Voice)
        length += MP3(f"assets/mp3/posttext.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"])):

        #allow user to see what comment is being saved
        print_substep(f"Saving MP3 {idx + 1} ")

        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break

        comment = comment["comment_body"]
        text = re.sub('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', '', comment)
        
        TTS.tts(text, f"./assets/mp3/{idx}.mp3", Voice)
        length += MP3(f"./assets/mp3/{idx}.mp3").info.length
    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
