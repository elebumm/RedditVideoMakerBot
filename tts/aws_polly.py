#!/usr/bin/env python3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import sys

max_chars = 0

def run(text, filepath):
    session = Session(profile_name="polly")
    polly = session.client("polly")

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
        file = open(filepath, 'wb')
        file.write(response['AudioStream'].read())
        file.close()
        #print_substep(f"Saved Text {idx} to MP3 files successfully.", style="bold green")

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)
