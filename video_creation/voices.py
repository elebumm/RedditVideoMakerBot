from TTS.engine_wrapper import TTSEngine
from TTS.GTTS import GTTS
from TTS.streamlabs_polly import StreamlabsPolly
from TTS.aws_polly import AWSPolly
from TTS.TikTok import TikTok
from utils import settings
from utils.console import print_table, print_step


TTSProviders = {
    "GoogleTranslate": GTTS,
    "AWSPolly": AWSPolly,
    "StreamlabsPolly": StreamlabsPolly,
    "TikTok": TikTok,
}


def save_text_to_mp3(
        reddit_obj: dict,
) -> list:
    """Saves text to MP3 files.

    Args:
        reddit_obj (): Reddit object received from reddit API in reddit/subreddit.py

    Returns:
        The number of comments audio was generated for
    """

    voice = settings.config["settings"]["tts"]["choice"]
    if voice.casefold() not in map(lambda _: _.casefold(), TTSProviders):
        while True:
            print_step("Please choose one of the following TTS providers: ")
            print_table(TTSProviders)
            voice = input("\n")
            if voice.casefold() in map(lambda _: _.casefold(), TTSProviders):
                break
            print("Unknown Choice")
    engine_instance = TTSEngine(get_case_insensitive_key_value(TTSProviders, voice), reddit_obj)
    return engine_instance.run()


def get_case_insensitive_key_value(input_dict, key):
    return next(
        (value for dict_key, value in input_dict.items() if dict_key.lower() == key.lower()),
        None,
    )
