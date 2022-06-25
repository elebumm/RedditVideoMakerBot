#!/usr/bin/env python3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import sys
import os
import random

voices = [
    "Brian",
    "Emma",
    "Russell",
    "Joey",
    "Matthew",
    "Joanna",
    "Kimberly",
    "Amy",
    "Geraint",
    "Nicole",
    "Justin",
    "Ivy",
    "Kendra",
    "Salli",
    "Raveena",
]


class AWSPolly:
    def __init__(self):
        self.max_chars = 0
        self.voices = voices

    def run(self, text, filepath, random_voice: bool = False):
        session = Session(profile_name="polly")
        polly = session.client("polly")
        if random_voice:
            voice = self.randomvoice()
        else:
            if not os.getenv("VOICE"):
                return ValueError(
                    f"Please set the environment variable VOICE to a valid voice. options are: {voices}"
                )
            voice = str(os.getenv("AWS_VOICE")).capitalize()
        try:
            # Request speech synthesis
            response = polly.synthesize_speech(
                Text=text, OutputFormat="mp3", VoiceId=voice, Engine="neural"
            )
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            print(error)
            sys.exit(-1)

        # Access the audio stream from the response
        if "AudioStream" in response:
            file = open(filepath, "wb")
            file.write(response["AudioStream"].read())
            file.close()
            # print_substep(f"Saved Text {idx} to MP3 files successfully.", style="bold green")

        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
            sys.exit(-1)

    def randomvoice(self):
        return random.choice(self.voices)
