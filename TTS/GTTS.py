#!/usr/bin/env python3
import random
import os
from gtts import gTTS

max_chars = 0


class GTTS:
    def __init__(self):
        self.max_chars = 0
        self.voices = []

    def run(self, text, filepath):
        tts = gTTS(text=text, lang=os.getenv("POSTLANG") or "en", slow=False)
        tts.save(filepath)

    def randomvoice(self):
        return random.choice(self.voices)
