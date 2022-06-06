#!/usr/bin/env python3
from gtts import gTTS

max_chars = 0


def run(text, filepath):
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(filepath)
