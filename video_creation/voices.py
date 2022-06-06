from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import os
import sys
import subprocess
from tempfile import gettempdir

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0
    session = Session(profile_name="polly")
    polly = session.client("polly")

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    text_to_speech(polly, "title", reddit_obj["thread_title"])
    length += MP3(f"assets/mp3/title.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break

        text_to_speech(polly, idx, comment["comment_body"])

        length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep(f"Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx

def text_to_speech(polly, idx, text):

    try:
    # Request speech synthesis
        response = polly.synthesize_speech(Text=text, OutputFormat="mp3",
                                            VoiceId="Joanna", Engine = 'neural')
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        output = f"assets/mp3/{idx}.mp3"
        file = open(output, 'wb')
        file.write(response['AudioStream'].read())
        file.close()
        #print_substep(f"Saved Text {idx} to MP3 files successfully.", style="bold green")

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
