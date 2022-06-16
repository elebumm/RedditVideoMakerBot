from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track


def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files

    Args:
        reddit_obj (dict): Reddit object given by get_subreddit_threads

    Returns:
        tuple[int,int]: First index is the video length in seconds, I don't know what the second thing is
    """

    print_step("Saving Text to MP3 files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    # Generate title audio and add to length
    length += save_audio(
        reddit_obj["thread_title"], f"assets/mp3/title.mp3", lang="en", slow=False)

    try:
        Path(f"assets/mp3/posttext.mp3").unlink()
    except OSError as e:
        pass

    # Generates the thread post audio
    if reddit_obj["thread_post"] != "":
        length += save_audio(
            reddit_obj["thread_post"], f"assets/mp3/posttext.mp3", lang="en", slow=False)

    # Generates each comment's audio
    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break
        length += save_audio(
            comment["comment_body"], f"assets/mp3/{idx}.mp3", lang="en", slow=False)

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx


def save_audio(text, filepath, **gtts_kwargs):
    """Generates and saves audio

    Args:
        text (str): Text to be saved as an MP3
        filepath (str): Path to save the file to

    Returns:
        int: Length of the clip generated, in seconds
    """     

    tts = gTTS(text, **gtts_kwargs)
    tts.save(filepath)
    return MP3(filepath).info.length
