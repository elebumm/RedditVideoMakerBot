import random

from elevenlabs import save
from elevenlabs.client import ElevenLabs

from utils import settings


class elevenlabs:
    def __init__(self):
        self.max_chars = 2500
        self.client: ElevenLabs = None

    def run(self, text, filepath, random_voice: bool = False):
        if self.client is None:
            self.initialize()
        if random_voice:
            voice = self.randomvoice()
        else:
            voice = str(settings.config["settings"]["tts"]["elevenlabs_voice_name"]).capitalize()

        audio = self.client.generate(text=text, voice=voice, model="eleven_multilingual_v1")
        save(audio=audio, filename=filepath)

    def initialize(self):
        if settings.config["settings"]["tts"]["elevenlabs_api_key"]:
            api_key = settings.config["settings"]["tts"]["elevenlabs_api_key"]
        else:
            raise ValueError(
                "You didn't set an Elevenlabs API key! Please set the config variable ELEVENLABS_API_KEY to a valid API key."
            )

        self.client = ElevenLabs(api_key=api_key)

    def randomvoice(self):
        if self.client is None:
            self.initialize()
        return random.choice(self.client.voices.get_all().voices).name
