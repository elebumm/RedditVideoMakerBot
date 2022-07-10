#!/usr/bin/env python3
from pathlib import Path
from typing import Tuple
import re
import time
import os
# import sox
# from mutagen import MutagenError
# from mutagen.mp3 import MP3, HeaderNotFoundError
import translators as ts
from rich.progress import track
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
from utils.console import print_step, print_substep
from utils.voice import sanitize_text
from utils import settings

DEFUALT_MAX_LENGTH: int = 50  # video length variable


class TTSEngine:

    """Calls the given TTS engine to reduce code duplication and allow multiple TTS engines.

    Args:
        tts_module          : The TTS module. Your module should handle the TTS itself and saving to the given path under the run method.
        reddit_object         : The reddit object that contains the posts to read.
        path (Optional)       : The unix style path to save the mp3 files to. This must not have leading or trailing slashes.
        max_length (Optional) : The maximum length of the mp3 files in total.

    Notes:
        tts_module must take the arguments text and filepath.
    """

    def __init__(
        self,
        tts_module,
        reddit_object: dict,
        path: str = "assets/temp/mp3",
        max_length: int = DEFUALT_MAX_LENGTH,
    ):
        self.tts_module = tts_module()
        self.reddit_object = reddit_object
        self.path = path
        self.max_length = max_length
        self.length = 0

    def run(self) -> Tuple[int, int]:

        Path(self.path).mkdir(parents=True, exist_ok=True)

        # This file needs to be removed in case this post does not use post text, so that it wont appear in the final video
        try:
            Path(f"{self.path}/posttext.mp3").unlink()
        except OSError:
            pass

        print_step("Saving Text to MP3 files...")

        self.call_tts("title", self.reddit_object["thread_title"])
        if (
            self.reddit_object["thread_post"] != ""
            and settings.config["settings"]["storymode"] == True
        ):
            self.call_tts("posttext", self.reddit_object["thread_post"])

        idx = None
        for idx, comment in track(enumerate(self.reddit_object["comments"]), "Saving..."):
            # ! Stop creating mp3 files if the length is greater than max length.
            if self.length > self.max_length:
                break
            if not self.tts_module.max_chars:
                self.call_tts(f"{idx}", comment["comment_body"])
            else:
                # THESE TRY EXCEPTS SOMEHOW SOLVES FFMPEG ERROR #
                try:
                    self.split_post(comment["comment_body"], idx)
                except:
                    print('Error, removing '+f"{self.path}/{idx}-0.part.mp3") # It still continues
                    try:
                        os.remove(f"{self.path}/{idx}-0.part.mp3")
                    except:
                        pass


        print_substep("Saved Text to MP3 files successfully.", style="bold green")
        return self.length, idx

    def split_post(self, text: str, idx: int):
        split_files = []
        split_text = [
            x.group().strip()
            for x in re.finditer(rf" *((.{{0,{self.tts_module.max_chars}}})(.$| $|\n | \n))", text)
        ]

        idy = None
        for idy, text_cut in enumerate(split_text):
            # print(f"{idx}-{idy}: {text_cut}\n")
            self.call_tts(f"{idx}-{idy}.part", text_cut)
            # THESE TRY EXCEPTS SOMEHOW SOLVES FFMPEG ERROR #
            try:
                split_files.append(AudioFileClip(f"{self.path}/{idx}-{idy}.part.mp3"))
            except:
                print('Error, removing '+f"{self.path}/{idx}-{idy}.part.mp3")
                try:
                    os.remove(f"{self.path}/{idx}-{idy}.part.mp3")
                except:
                    pass
        ### !!! Without the following sleep (preferably 1sec), sometimes a part seem to be missing, causing errors or bad renders, 
        #feel free to try for example same thread 500 times and see how many times it renders the same amount of .mp3 files (not parts), 
        #can probably build a tracker for this to count how many times each part renders !!! ###
        time.sleep(0.5) 
        CompositeAudioClip([concatenate_audioclips(split_files)]).write_audiofile(
            f"{self.path}/{idx}.mp3", fps=44100, verbose=False, logger=None
        )
        for i in split_files:
            name = i.filename
            i.close()
            Path(name).unlink()

        # for i in range(0, idy + 1):
        # print(f"Cleaning up {self.path}/{idx}-{i}.part.mp3")

        # Path(f"{self.path}/{idx}-{i}.part.mp3").unlink()

    def call_tts(self, filename: str, text: str):
        self.tts_module.run(text=process_text(text), filepath=f"{self.path}/{filename}.mp3")
        # try:
        #     self.length += MP3(f"{self.path}/{filename}.mp3").info.length
        # except (MutagenError, HeaderNotFoundError):
        #     self.length += sox.file_info.duration(f"{self.path}/{filename}.mp3")
        try:
            clip = AudioFileClip(f"{self.path}/{filename}.mp3")
            self.length += clip.duration
            clip.close()
        except:
            self.length = 0

def process_text(text: str):
    lang = settings.config["reddit"]["thread"]["post_lang"]
    new_text = sanitize_text(text)
    if lang:
        print_substep("Translating Text...")
        translated_text = ts.google(text, to_language=lang)
        new_text = sanitize_text(translated_text)
    return new_text
