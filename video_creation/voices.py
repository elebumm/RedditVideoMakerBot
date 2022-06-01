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
    print_step("Saving Text to MP3 files 🎶")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    if voice == "female":
        tts = gTTS(text=reddit_obj["thread_title"], lang="en", slow=False, tld="co.uk")
        tts.save(f"assets/mp3/title.mp3")
    elif voice == "male":
        url = 'https://streamlabs.com/polly/speak'
        body = {'voice': 'Brian', 'text': reddit_obj["thread_title"]}
        response = requests.post(url, data = body)
        voice_data = requests.get(response.json()['speak_url'])
        f = open('assets/mp3/title.mp3', 'wb')
        f.write(voice_data.content)

    length += MP3(f"assets/mp3/title.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break

        if voice == "female":
            tts = gTTS(text=comment["comment_body"], lang="en")
            tts.save(f"assets/mp3/{idx}.mp3")
        elif voice == "male":
            body = {'voice': 'Brian', 'text': comment["comment_body"]}
            response = requests.post(url, data = body)
            voice_data = requests.get(response.json()['speak_url'])
            f = open(f"assets/mp3/{idx}.mp3", 'wb')
            f.write(voice_data.content)

        length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep("Saved Text to MP3 files Successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
