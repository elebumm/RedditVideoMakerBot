import random

import pyttsx3

from utils import settings

from typing import Optional


class pyttsx:
    def __init__(self):
        self.max_chars = 5000
        self.voices = []

    def run(
        self,
        text: str,
        filepath: str,
        random_voice=False,
        voice: Optional[str] = None,
    ):
        voice_id = settings.config["settings"]["tts"]["python_voice"]
        voice_num = settings.config["settings"]["tts"]["py_voice_num"]

        if not voice:
            if random_voice:
                voice = self.random_voice()
            else:
                # if pyTTS is not set in the config file, then use a random voice
                voice = settings.config["settings"]["tts"].get("python_voice", self.random_voice())
        if voice_id == "" or voice_num == "":
            voice_id = 2
            voice_num = 3
            raise ValueError(
                "set pyttsx values to a valid value, switching to defaults"
            )
        else:
            voice_id = int(voice_id)
            voice_num = int(voice_num)
        for i in range(voice_num):
            self.voices.append(i)
            i = +1
        if random_voice:
            voice_id = self.randomvoice()
        engine = pyttsx3.init()
        engine.save_to_file(text, f"{filepath}")
        engine.runAndWait()

    def random_voice(self):
        return random.choice(self.voices)