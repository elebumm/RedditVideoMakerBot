from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track

class TTSEngine:

    """Calls the given TTS engine to reduce code duplication and allow multiple TTS engines.
    Args:
        tts_function          : The function that will be called. Your function should handle the TTS itself and saving to the given path.
        reddit_object         : The reddit object that contains the posts to read.
        path (Optional)       : The unix style path to save the mp3 files to. This must not have leading or trailing slashes.
        max_length (Optional) : The maximum length of the mp3 files in total.
    Notes:
        tts_function must take the parameters text and filepath as arguments.
    """

    def __init__(self, tts_function: function, reddit_object, path: str = "assets/mp3", max_length: int = 50):
        self.tts_function = tts_function
        self.reddit_object = reddit_object
        self.path = path
        self.max_length = max_length
        self.length = 0
