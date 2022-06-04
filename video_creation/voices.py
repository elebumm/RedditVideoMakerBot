from pathlib import Path
from utils.console import print_step, print_substep
from rich.progress import track
import pyttsx3
from dotenv import load_dotenv
import os
import librosa

load_dotenv()

VoiceGender = os.getenv('VoiceGender')


def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # create the object
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('volume', 1.0) 

    # Set the voice depending on what was set in .env
    if VoiceGender == 'male':
        engine.setProperty('voice', voices[0].id)
    elif VoiceGender == 'female':
        engine.setProperty('voice', voices[1].id)
    # if nothing set default to female voice
    else:
        engine.setProperty('voice', voices[1].id)


    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    engine.save_to_file(str(reddit_obj["thread_title"]), "./assets/mp3/title.mp3")
    engine.runAndWait()
    length += librosa.get_duration(filename='./assets/mp3/title.mp3')

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break

        engine.save_to_file(str(comment["comment_body"]), f"./assets/mp3/{idx}.mp3")
        engine.runAndWait()
        length += librosa.get_duration(filename=f'./assets/mp3/{idx}.mp3')
    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
