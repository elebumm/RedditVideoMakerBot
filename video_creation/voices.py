from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track
import requests


def save_text_to_mp3(reddit_obj, voice):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    generate_and_save_tts(voice, reddit_obj["thread_title"], "assets/mp3/title.mp3")
    length += MP3(f"assets/mp3/title.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break

        generate_and_save_tts(voice, comment["comment_body"], f"assets/mp3/{idx}.mp3")
        length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx

def generate_and_save_tts(voice, text, file_name):
    if voice == "female":
        tts = gTTS(text=text, lang="en")
        tts.save(file_name)
    elif voice == "male":
        url = 'https://streamlabs.com/polly/speak'
        body = {'voice': 'Brian', 'text': text}
        response = requests.post(url, data = body)
        voice_data = requests.get(response.json()['speak_url'])
        f = open(file_name, 'wb')
        f.write(voice_data.content)