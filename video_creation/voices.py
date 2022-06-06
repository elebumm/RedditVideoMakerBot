from utils.console import print_step, print_substep
from rich.progress import track
from tts.engine_wrapper import TTSEngine
import tts.google_translate_tts

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    text_to_mp3 = TTSEngine(tts.google_translate_tts, reddit_obj)
    return text_to_mp3.run()
