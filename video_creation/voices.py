import os
from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track


def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files 🎶")

    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        from google.cloud import texttospeech

    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        client = texttospeech.TextToSpeechClient()

        thread_title = texttospeech.SynthesisInput(text=reddit_obj["thread_title"])
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB", name="en-GB-Wavenet-D"
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            request={
                "input": thread_title,
                "voice": voice,
                "audio_config": audio_config,
            }
        )
        with open("assets/mp3/title.mp3", "wb") as out:
            out.write(response.audio_content)
        length += MP3(f"assets/mp3/title.mp3").info.length

        for idx, comment in track(
            enumerate(reddit_obj["comments"]), "Saving comments to MP3 files"
        ):
            if length > 35:
                break
            comment_body = texttospeech.SynthesisInput(text=comment["comment_body"])
            response = client.synthesize_speech(
                request={
                    "input": comment_body,
                    "voice": voice,
                    "audio_config": audio_config,
                }
            )
            with open(f"assets/mp3/{idx}.mp3", "wb") as out:
                out.write(response.audio_content)
            length += MP3(f"assets/mp3/{idx}.mp3").info.length

        return length, idx

    tts = gTTS(text=reddit_obj["thread_title"], lang="en", slow=False, tld="co.uk")
    tts.save(f"assets/mp3/title.mp3")
    length += MP3(f"assets/mp3/title.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 35:
            break
        tts = gTTS(text=comment["comment_body"], lang="en")
        tts.save(f"assets/mp3/{idx}.mp3")
        length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep("Saved Text to MP3 files Successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
