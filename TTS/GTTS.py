#!/usr/bin/env python3
from utils import settings
from gtts import gTTS


class GTTS:
    max_chars = 0
    # voices = []

    @staticmethod
    def run(
            text,
            filepath
    ) -> None:
        """
        Calls for TTS api

        Args:
            text: text to be voiced over
            filepath: name of the audio file
        """
        tts = gTTS(
            text=text,
            lang=settings.config["reddit"]["thread"]["post_lang"] or "en",
            slow=False,
        )
        tts.save(filepath)
