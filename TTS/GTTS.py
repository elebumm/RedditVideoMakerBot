import random

from gtts import gTTS

from utils import settings

from typing import Optional


class GTTS:
    def __init__(self):
        self.max_chars = 5000
        self.voices = []

    def run(self, text, filepath, random_voice: bool = False, voice: Optional[str] = None):
        tts = gTTS(
            text=text,
            lang=settings.config["reddit"]["thread"]["post_lang"] or "en",
            slow=False,
        )
        tts.save(filepath)

    def random_voice(self):
        return random.choice(self.voices)