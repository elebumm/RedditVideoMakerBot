#!/usr/bin/env python3
from pathlib import Path
from typing import Union

import translators as ts
from rich.progress import track
from attr import attrs, attrib

from utils.console import print_step, print_substep
from utils.voice import sanitize_text
from utils import settings
from TTS.common import audio_length

from TTS.GTTS import GTTS
from TTS.streamlabs_polly import StreamlabsPolly
from TTS.TikTok import TikTok
from TTS.aws_polly import AWSPolly


@attrs
class TTSEngine:
    """Calls the given TTS engine to reduce code duplication and allow multiple TTS engines.

    Args:
        tts_module          : The TTS module. Your module should handle the TTS itself and saving to the given path under the run method.
        reddit_object         : The reddit object that contains the posts to read.

    Notes:
        tts_module must take the arguments text and filepath.
    """
    tts_module: Union[GTTS, StreamlabsPolly, TikTok, AWSPolly] = attrib()
    reddit_object: dict = attrib()
    __path: str = "assets/temp/mp3"
    __total_length: int = 0

    def __attrs_post_init__(self):
        # Calls an instance of the tts_module class
        self.tts_module = self.tts_module()
        # Loading settings from the config
        self.max_length: int = settings.config["settings"]["video_length"]
        self.time_before_tts: float = settings.config["settings"]["time_before_tts"]
        self.time_between_pictures: float = settings.config["settings"]["time_between_pictures"]
        self.__total_length = (
                settings.config["settings"]["time_before_first_picture"] +
                settings.config["settings"]["delay_before_end"]
        )

    def run(
            self
    ) -> list:
        """
        Voices over comments & title of the submission

        Returns:
            Indexes of comments to be used in the final video
        """
        Path(self.__path).mkdir(parents=True, exist_ok=True)

        # This file needs to be removed in case this post does not use post text
        # so that it won't appear in the final video
        try:
            Path(f"{self.__path}/posttext.mp3").unlink()
        except OSError:
            pass

        print_step("Saving Text to MP3 files...")

        self.call_tts("title", self.reddit_object["thread_title"])

        if self.reddit_object["thread_post"] and settings.config["settings"]["storymode"]:
            self.call_tts("posttext", self.reddit_object["thread_post"])

        sync_tasks_primary = [
            self.call_tts(str(idx), comment["comment_body"])
            for idx, comment in track(
                enumerate(self.reddit_object["comments"]),
                description="Saving...",
                total=self.reddit_object["comments"].__len__())
            # Crunch, there will be fix in async TTS api, maybe
            if self.__total_length + self.__total_length * 0.05 < self.max_length
        ]

        print_substep("Saved Text to MP3 files successfully.", style="bold green")
        return [
            comments for comments, condition in
            zip(range(self.reddit_object["comments"].__len__()), sync_tasks_primary)
            if condition
        ]

    def call_tts(
            self,
            filename: str,
            text: str
    ) -> bool:
        """
        Calls for TTS api from the factory

        Args:
            filename: name of audio file w/o .mp3
            text: text to be voiced over

        Returns:
            True if audio files not exceeding the maximum length else false
        """
        if not text:
            return False

        self.tts_module.run(
            text=self.process_text(text),
            filepath=f"{self.__path}/{filename}.mp3"
        )

        clip_length = audio_length(f"{self.__path}/{filename}.mp3")
        clip_offset = self.time_between_pictures + self.time_before_tts * 2

        if clip_length and self.__total_length + clip_length + clip_offset <= self.max_length:
            self.__total_length += clip_length + clip_offset
            return True
        return False

    @staticmethod
    def process_text(
            text: str,
    ) -> str:
        """
        Sanitizes text for illegal characters and translates text

        Args:
            text: text to be sanitized & translated

        Returns:
            Processed text as a str
        """
        lang = settings.config["reddit"]["thread"]["post_lang"]
        new_text = sanitize_text(text)
        if lang:
            print_substep("Translating Text...")
            translated_text = ts.google(text, to_language=lang)
            new_text = sanitize_text(translated_text)
        return new_text
