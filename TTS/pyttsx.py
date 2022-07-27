import pyttsx3
from utils import settings
import random

max_chars = 0

#Uses the system voices, significantly faster than other tts

class pyttsx:

    def __init__(self):
        self.max_chars = 0
        self.voices = []

    def run(
        self,
        text: str = "Python Text to Speech",
        filepath: str = "assets/temp/mp3",
        random_voice=False,
        censor=False,
    ):
        voice_id = int(settings.config["settings"]["tts"]["python_voice"])
        voice_num = int(settings.config["settings"]["tts"]["python_voice_number"])
        for i in range(voice_num-1):
            self.voices.append(i)
            i=+1
        if random_voice:
            voice_id = self.randomvoice()
        else:
            voice = voice_id
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[voice].id) #changing index changes voices but ony 0 and 1 are working here
        engine.save_to_file(text, f"{filepath}")
        engine.runAndWait()
    
    def randomvoice(self):
        return random.choice(self.voices)