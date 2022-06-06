import os
from utils.console import print_step, print_substep
from rich.progress import track
from tts.engine_wrapper import TTSEngine
import tts.google_translate_tts

## Add your provider here on a new line
TTSProviders ={
    "GoogleTranslate": tts.google_translate_tts
}

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    text_to_mp3 = TTSEngine(tts.google_translate_tts, reddit_obj)
    return text_to_mp3.run()


def get_case_insensitive_key_value(input_dict, key):
    return next((value for dict_key, value in input_dict.items() if dict_key.lower() == key.lower()), None)