import random
import os
import requests
from requests.exceptions import JSONDecodeError

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


# valid voices https://lazypy.ro/tts/


class StreamlabsPolly:
    def __init__(self):
        self.url = "https://streamlabs.com/polly/speak"
        self.max_chars = 349
        self.voices = voices

    def run(self, text, filepath, random_voice: bool = False):
        if random_voice:
            voice = self.randomvoice()
        else:
            if not os.getenv("VOICE"):
                return ValueError(
                    f"Please set the environment variable VOICE to a valid voice. options are: {voices}"
                )
            voice = str(os.getenv("STREAMLABS_VOICE")).capitalize()
        body = {"voice": voice, "text": text, "service": "polly"}
        response = requests.post(self.url, data=body)
        try:
            voice_data = requests.get(response.json()["speak_url"])
            with open(filepath, "wb") as f:
                f.write(voice_data.content)
        except (KeyError, JSONDecodeError):
            print("Error occured calling Streamlabs Polly")

    def randomvoice(self):
        return random.choice(self.voices)
