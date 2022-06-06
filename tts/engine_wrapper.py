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
        tts_function must take the arguments text and filepath.
    """

    def __init__(self, tts_function: function, reddit_object: dict, path: str = "assets/mp3", max_length: int = 50):
        self.tts_function = tts_function
        self.reddit_object = reddit_object
        self.path = path
        self.max_length = max_length
        self.length = 0

    def run(self):

        Path(self.path).mkdir(parents=True, exist_ok=True)

        # This file needs to be removed in case this post does not use post text, so that it wont appear in the final video
        try:
            Path(f"{self.path}/posttext.mp3").unlink()
        except OSError as e:
            pass

        print_step("Saving Text to MP3 files...")

        self.call_tts("title", self.reddit_object["thread_title"])

        if self.reddit_object["thread_post"] != "":
            self.call_tts("posttext", self.reddit_object["thread_post"])

        for idx, comment in track(enumerate(self.reddit_object["comments"]), "Saving..."):
            # ! Stop creating mp3 files if the length is greater than max length.
            if self.length > self.max_length:
                break

            self.call_tts(f"{idx}",comment["comment_body"])

        print_substep("Saved Text to MP3 files successfully.", style="bold green")
        return self.length, idx

    def call_tts(self, filename, text):
        self.tts_function(text=text, filepath=f"{self.path}/{filename}.mp3")
        self.length += MP3(f"{self.path}/{filename}.mp3").info.length
