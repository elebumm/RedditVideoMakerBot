import requests
from requests.exceptions import JSONDecodeError
from utils import settings
from attr import attrs, attrib
from attr.validators import instance_of

from TTS.common import BaseApiTTS, get_random_voice
from utils.voice import check_ratelimit

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


@attrs
class StreamlabsPolly(BaseApiTTS):
    random_voice: bool = attrib(
        validator=instance_of(bool),
        default=False
    )
    url: str = "https://streamlabs.com/polly/speak"
    max_chars: int = 550

    def make_request(
            self,
            text,
    ):
        """
        Makes a requests to remote TTS service

        Args:
            text: text to be voice over

        Returns:
            Request's response
        """
        voice = (
            get_random_voice(voices)
            if self.random_voice
            else str(settings.config["settings"]["tts"]["streamlabs_polly_voice"]).capitalize()
            if str(settings.config["settings"]["tts"]["streamlabs_polly_voice"]).lower() in [
                voice.lower() for voice in voices]
            else get_random_voice(voices)
        )
        response = requests.post(
            self.url,
            data={
                "voice": voice,
                "text": text,
                "service": "polly",
            })
        if not check_ratelimit(response):
            return self.make_request(text)
        else:
            try:
                results = requests.get(response.json()["speak_url"])
                return results.content
            except (KeyError, JSONDecodeError):
                try:
                    if response.json()["error"] == "No text specified!":
                        raise ValueError("Please specify a text to convert to speech.")
                except (KeyError, JSONDecodeError):
                    print("Error occurred calling Streamlabs Polly")
