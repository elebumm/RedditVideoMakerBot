import pyttsx3
from pathlib import Path
from mutagen.wave import WAVE
from utils.console import print_step, print_substep
from rich.progress import track


def save_text_to_wav(reddit_obj):
    """Saves Text to WAV files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to WAV files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/wav").mkdir(parents=True, exist_ok=True)

    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    engine.save_to_file(reddit_obj["thread_title"], f"assets/wav/title.wav")
    engine.runAndWait()
    length += WAVE(f"assets/wav/title.wav").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating wav files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break
        engine.save_to_file(comment["comment_body"], f"assets/wav/{idx}.wav")
        engine.runAndWait()
        length += WAVE(f"assets/wav/{idx}.wav").info.length

    print_substep("Saved Text to WAV files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
