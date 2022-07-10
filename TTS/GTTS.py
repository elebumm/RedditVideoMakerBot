#!/usr/bin/env python3
from utils import settings
from gtts import gTTS


class GTTS:
    max_chars = 0

    @staticmethod
    async def run(
            text,
            filepath
    ) -> None:
        tts = gTTS(
            text=text,
            lang=settings.config["reddit"]["thread"]["post_lang"] or "en",
            slow=False,
        )
        tts.save(filepath)
