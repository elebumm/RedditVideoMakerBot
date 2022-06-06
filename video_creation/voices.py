# from gtts import gTTS
import pyttsx3
from pathlib import Path
from utils.console import print_step, print_substep
from rich.progress import track
import audioread

def save_text_to_mp3(reddit_obj, voices, selected_voice):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    if not selected_voice:
        selected_voice = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    # tts = gTTS(text=reddit_obj["thread_title"], lang="en", slow=False)
    # tts.save(f"assets/mp3/title.mp3")
    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    engine.setProperty("voice", voices[selected_voice].id)
    engine.save_to_file(reddit_obj["thread_title"], f"assets/mp3/title.mp3")
    engine.runAndWait()

    # length += MP3(f"assets/mp3/title.mp3").info.length
    length += audioread.audio_open(f"assets/mp3/title.mp3").duration

    try:
        Path(f"assets/mp3/posttext.mp3").unlink()
    except OSError as e:
        pass

    if reddit_obj["thread_post"] != "":
        # tts = gTTS(text=reddit_obj["thread_post"], lang="en", slow=False)
        # tts.save(f"assets/mp3/posttext.mp3")
        engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        engine.setProperty("voice", voices[selected_voice].id)
        engine.save_to_file(reddit_obj["thread_post"], f"assets/mp3/posttext.mp3")
        engine.runAndWait()


        # length += MP3(f"assets/mp3/posttext.mp3").info.length
        length += audioread.audio_open(f"assets/mp3/posttext.mp3").duration

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break
        # tts = gTTS(text=comment["comment_body"], lang="en", slow=False)
        # tts.save(f"assets/mp3/{idx}.mp3")
        engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        engine.setProperty("voice", voices[selected_voice].id)
        engine.save_to_file(comment["comment_body"], f"assets/mp3/{idx}.mp3")
        engine.runAndWait()

        # length += MP3(f"assets/mp3/{idx}.mp3").info.length
        length += audioread.audio_open(f"assets/mp3/{idx}.mp3").duration

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
