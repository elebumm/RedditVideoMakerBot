import random

from gtts import gTTS

from utils import settings


class GTTS:
    def __init__(self):
        self.max_chars = 5000
        self.voices = []

    def run(self, text, filepath, random_voice: bool = False):
        # Support both Threads and Reddit config for language
        lang = "en"
        if "threads" in settings.config and "thread" in settings.config["threads"]:
            lang = settings.config["threads"]["thread"].get("post_lang", "") or lang
        elif "reddit" in settings.config and "thread" in settings.config["reddit"]:
            lang = settings.config["reddit"]["thread"].get("post_lang", "") or lang
        tts = gTTS(
            text=text,
            lang=lang,
            slow=False,
        )
        tts.save(filepath)

    def randomvoice(self):
        return random.choice(self.voices)
