import random

import pyttsx3

from utils import settings


class pyttsx:
    def __init__(self):
        self.max_chars = 5000
        self.voices = []
        engine = pyttsx3.init()
        self.voices = [voice.id for voice in engine.getProperty("voices")]

    def run(self, text: str, filepath: str, random_voice=False, voice=None):
        voice_id = voice or settings.config["settings"]["tts"]["python_voice"]

        if not voice_id:
            voice_id = self.random_voice()

        if not voice_id.isdigit():
            raise ValueError("Invalid voice ID provided")
        voice_id = int(voice_id)

        if voice_id >= len(self.voices):
            raise ValueError(f"Voice ID out of range. Valid IDs are 0 to {len(self.voices) - 1}")

        if random_voice:
            voice_id = self.random_voice()

        engine = pyttsx3.init()
        engine.setProperty("voice", self.voices[voice_id])
        engine.save_to_file(text, f"{filepath}")
        engine.runAndWait()

    def random_voice(self):
        return random.choice(self.voices)