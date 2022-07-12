#!/usr/bin/env python3
from pathlib import Path
from typing import Tuple
import re

# import sox
# from mutagen import MutagenError
# from mutagen.mp3 import MP3, HeaderNotFoundError
import translators as ts
from rich.progress import track
from attr import attrs, attrib

from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips

from utils.console import print_step, print_substep
from utils.voice import sanitize_text
from utils import settings
from TTS.common import audio_length


@attrs(auto_attribs=True)
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
    tts_module: object
    reddit_object: dict
    path: str = 'assets/temp/mp3'
    max_length: int = 50  # TODO move to config
    __total_length: int = attrib(
        default=0,
        kw_only=True
    )

    def run(
            self
    ) -> list:

        Path(self.path).mkdir(parents=True, exist_ok=True)

        # This file needs to be removed in case this post does not use post text
        # so that it won't appear in the final video
        try:
            Path(f'{self.path}/posttext.mp3').unlink()
        except OSError:
            pass

        print_step('Saving Text to MP3 files...')

        self.call_tts('title', self.reddit_object['thread_title'])

        if self.reddit_object['thread_post'] and settings.config['settings']['storymode']:
            self.call_tts('posttext', self.reddit_object['thread_post'])

        sync_tasks_primary = [
            self.call_tts(str(idx), comment['comment_body'])
            for idx, comment in track(enumerate(self.reddit_object['comments']), description='Saving...')
            # Crunch, there will be fix in async TTS api
            if self.__total_length + self.__total_length * 0.05 < self.max_length
        ]

        print_substep('Saved Text to MP3 files successfully.', style='bold green')
        return [
            comments for comments, condition in
            zip(range(self.reddit_object['comments'].__len__()), sync_tasks_primary)
            if condition
        ]

    def split_post(self, text: str, idx: int):
        split_files = []
        split_text = [
            x.group().strip()
            for x in re.finditer(
                r" *(((.|\n){0," + str(self.tts_module().max_chars) + "})(\.|.$))", text
            )
        ]
        offset = 0
        for idy, text_cut in enumerate(split_text):
            # print(f"{idx}-{idy}: {text_cut}\n")
            if not text_cut or text_cut.isspace():
                offset += 1
                continue

            self.call_tts(f"{idx}-{idy - offset}.part", text_cut)
            split_files.append(AudioFileClip(f"{self.path}/{idx}-{idy - offset}.part.mp3"))

        CompositeAudioClip([concatenate_audioclips(split_files)]).write_audiofile(
            f"{self.path}/{idx}.mp3", fps=44100, verbose=False, logger=None
        )

        for i in split_files:
            name = i.filename
            i.close()
            Path(name).unlink()

    def call_tts(
            self,
            filename: str,
            text: str
    ) -> bool:
        if not text:
            return False

        self.tts_module().run(
            text=self.process_text(text),
            filepath=f'{self.path}/{filename}.mp3'
        )

        clip_length = audio_length(f'assets/temp/mp3/{filename}.mp3')

        if clip_length and self.__total_length + clip_length <= self.max_length:
            self.__total_length += clip_length
            return True
        return False

    @staticmethod
    def process_text(
            text: str,
    ) -> str:
        lang = settings.config['reddit']['thread']['post_lang']
        new_text = sanitize_text(text)
        if lang:
            print_substep('Translating Text...')
            translated_text = ts.google(text, to_language=lang)
            new_text = sanitize_text(translated_text)
        return new_text
