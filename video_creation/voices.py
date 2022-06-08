#!/usr/bin/env python3
import os
from utils.console import print_step, print_substep, print_table
from tts.engine_wrapper import TTSEngine
import tts.google_translate


## Add your provider here on a new line
TTSProviders = {"GoogleTranslate": tts.google_translate}


def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    env = os.getenv("TTS_PROVIDER", "")
    if env in TTSProviders:
        text_to_mp3 = TTSEngine(env, reddit_obj)
    else:
        chosen = False
        choice = ""
        while not chosen:
            print("Please choose one of the following TTS providers: ")
            print_table(TTSProviders)
            choice = input("\n")
            if choice.casefold() not in map(lambda _: _.casefold(), TTSProviders):
                print("Unknown Choice")
            else:
                chosen = True
        text_to_mp3 = TTSEngine(
            get_case_insensitive_key_value(TTSProviders, choice), reddit_obj
        )

    return text_to_mp3.run()


def get_case_insensitive_key_value(input_dict, key):
    return next(
        (
            value
            for dict_key, value in input_dict.items()
            if dict_key.lower() == key.lower()
        ),
        None,
    )
