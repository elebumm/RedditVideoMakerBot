import random

import pyttsx3

from utils import settings


class pyttsx:
    def __init__(self):
        self.max_chars = 5000
        self.voices = []

    def run(
        self,
        text: str,
        filepath: str,
        random_voice=False,
    ):
        voice_id = settings.config["settings"]["tts"]["python_voice"]
        voice_num = settings.config["settings"]["tts"]["py_voice_num"]
        if voice_id == "" or voice_num == "":
            voice_id = 2
            voice_num = 3
            raise ValueError("set pyttsx values to a valid value, switching to defaults")
        else:
            voice_id = int(voice_id)
            voice_num = int(voice_num)
        for i in range(voice_num):
            self.voices.append(i)
            i = +1
        if random_voice:
            voice_id = self.randomvoice()
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        engine.setProperty(
            "voice", voices[voice_id].id
        )  # changing index changes voices but ony 0 and 1 are working here
        engine.save_to_file(text, f"{filepath}")
        engine.runAndWait()

    def randomvoice(self):
        return random.choice(self.voices)
