import random
import sys

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError, ProfileNotFound

from utils import settings

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
        self.max_chars = 3000
        self.voices = voices

    def run(self, text, filepath, random_voice: bool = False, voice: str = None):
        try:
            session = Session(profile_name="polly")
            polly = session.client("polly")

            if voice:  # If voice is explicitly provided, use it
                voice = voice.capitalize()
            elif random_voice:  # Else if random_voice is set to True, pick a random voice
                voice = self.random_voice()
            else:  # If none of the above, use the voice from the settings
                if not settings.config["settings"]["tts"]["aws_polly_voice"]:
                    raise ValueError(
                        f"Please set the TOML variable AWS_VOICE to a valid voice. options are: {voices}"
                    )
                voice = str(settings.config["settings"]["tts"]["aws_polly_voice"]).capitalize()
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
                with open(filepath, "wb") as file:
                    file.write(response["AudioStream"].read())
            else:
                # The response didn't contain audio data, exit gracefully
                print("Could not stream audio")
                sys.exit(-1)
        except ProfileNotFound:
            print("You need to install the AWS CLI and configure your profile")
            print(
                """
            Linux: https://docs.aws.amazon.com/polly/latest/dg/setup-aws-cli.html
            Windows: https://docs.aws.amazon.com/polly/latest/dg/install-voice-plugin2.html
            """
            )
            sys.exit(-1)

    def random_voice(self):
        return random.choice(self.voices)
