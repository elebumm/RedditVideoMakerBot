#!/usr/bin/env python3
from pathlib import Path
from typing import Tuple
import re

# import sox
# from mutagen import MutagenError
# from mutagen.mp3 import MP3, HeaderNotFoundError
import os

import numpy as np
from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.fx.volumex import volumex
import translators as ts
from rich.progress import track
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
from utils.console import print_step, print_substep
from utils.voice import sanitize_text
from utils import settings

DEFAULT_MAX_LENGTH: int = 45  # video length variable


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
        max_length: int = DEFAULT_MAX_LENGTH,
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
                self.split_post(comment["comment_body"], idx)

        print_substep("Saved Text to MP3 files successfully.", style="bold green")
        return self.length, idx

    def split_post(self, text: str, idx: int):
        split_text = [
            x.group().strip()
            for x in re.finditer(rf" *((.{{0,{self.tts_module.max_chars}}})(\.|.$))", text)
        ]
        try:
            silence_duration = settings.config["settings"]["tts"]["silence_duration"]
        except ValueError:
            silence_duration = 0.3

        silence_long = AudioClip(make_frame=lambda t: np.sin(440 * 2 * np.pi * t), duration=silence_duration, fps=44100)
        silence_long_new = volumex(silence_long, 0)
        silence_long_new.write_audiofile(f"{self.path}/long_silence.mp3", fps=44100, verbose=False, logger=None)

        idy = None
        for idy, text_cut in enumerate(split_text):
            print(f"{idx}-{idy}: {text_cut}\n")
            newtext = process_text(text_cut)
            #print(newtext)
            if not newtext or newtext.isspace():
                print("fuck you")
                break
            else:
                self.call_tts(f"{idx}-{idy}.part", newtext)
                with open(f"{self.path}/list.txt", 'w') as f:
                    for newy in range(0, len(split_text)):
                        f.write("file " + f"'{idx}-{newy}.part.mp3'" + "\n")
                    f.write("file " + f"'long_silence.mp3'" + "\n")

                os.system("ffmpeg -f concat -y -hide_banner -loglevel panic -safe 0 " +
                          "-i " + f"{self.path}/list.txt " +
                          "-c copy " + f"{self.path}/{idx}.mp3")
                try:
                    for i in range(0, idy + 1):
                        # print(f"Cleaning up {self.path}/{idx}-{i}.part.mp3")
                        Path(f"{self.path}/{idx}-{i}.part.mp3").unlink()
                except FileNotFoundError:
                    print("file not found error")

    def call_tts(self, filename: str, text: str):

        if filename == "title":
            self.tts_module.run(text, filepath=f"{self.path}/title_nosilence.mp3")


            silence_long = AudioClip(make_frame=lambda t: np.sin(440 * 2 * np.pi * t), duration=0.3,
                                     fps=44100)
            silence_long_new = volumex(silence_long, 0)
            silence_long_new.write_audiofile(f"{self.path}/title_silence.mp3", fps=44100, verbose=False, logger=None)

            with open(f"{self.path}/title.txt", 'w') as f:
                f.write("file " + f"'title_nosilence.mp3'"+"\n")
                f.write("file " + f"'title_silence.mp3'"+"\n")

            os.system("ffmpeg -f concat -y -hide_banner -loglevel panic -safe 0 " +
                      "-i " + f"{self.path}/title.txt " +
                      "-c copy " + f"{self.path}/title.mp3")


            clip = AudioFileClip(f"{self.path}/title.mp3")
            self.length += clip.duration
        else:
            self.tts_module.run(text=process_text(text), filepath=f"{self.path}/{filename}.mp3")
            clip = AudioFileClip(f"{self.path}/{filename}.mp3")
            self.length += clip.duration
        clip.close()


def process_text(text: str):
    lang = settings.config["reddit"]["thread"]["post_lang"]
    new_text = sanitize_text(text)
    if lang:
        print_substep("Translating Text...")
        translated_text = ts.google(text, to_language=lang)
        new_text = sanitize_text(translated_text)
    return new_text
