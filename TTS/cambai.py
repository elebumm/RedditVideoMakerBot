import random

from camb.client import CambAI, save_stream_to_file
from camb.types import StreamTtsOutputConfiguration

from utils import settings


class CambAITTS:
    def __init__(self):
        self.max_chars = 5000
        self.client: CambAI = None

    def run(self, text, filepath, random_voice: bool = False):
        if self.client is None:
            self.initialize()
        if random_voice:
            voice_id = self.randomvoice()
        else:
            voice_id = int(settings.config["settings"]["tts"]["cambai_voice_id"])

        language = str(
            settings.config["settings"]["tts"].get("cambai_language", "en-us")
        )
        speech_model = str(
            settings.config["settings"]["tts"].get("cambai_speech_model", "mars-flash")
        )

        stream = self.client.text_to_speech.tts(
            text=text,
            language=language,
            voice_id=voice_id,
            speech_model=speech_model,
            output_configuration=StreamTtsOutputConfiguration(format="mp3"),
        )
        save_stream_to_file(stream, filepath)

    def initialize(self):
        api_key = settings.config["settings"]["tts"].get("cambai_api_key", "")
        if not api_key:
            raise ValueError(
                "You didn't set a CAMB AI API key! Please set the config variable cambai_api_key to a valid API key."
            )
        self.client = CambAI(api_key=api_key)

    def randomvoice(self):
        if self.client is None:
            self.initialize()
        voices = self.client.voice_cloning.list_voices()
        return random.choice(voices)["id"]
