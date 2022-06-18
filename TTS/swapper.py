from os import getenv

from dotenv import load_dotenv

from TTS.GTTS import GTTS
from TTS.POLLY import POLLY
from TTS.TikTok import TikTok
from utils.console import print_substep

CHOICE_DIR = {"tiktok": TikTok, "gtts": GTTS, "polly": POLLY}


class TTS:
    def __new__(cls):
        load_dotenv()
        try:
            CHOICE = getenv("TTsChoice").casefold()
        except AttributeError:
            print_substep("None defined. Defaulting to 'polly.'")
            CHOICE = "polly"
        valid_keys = [key.lower() for key in CHOICE_DIR.keys()]
        if CHOICE not in valid_keys:
            raise ValueError(f"{CHOICE} is not valid. Please use one of these {valid_keys} options")
        return CHOICE_DIR.get(CHOICE)()
