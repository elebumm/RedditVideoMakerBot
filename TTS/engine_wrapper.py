#!/usr/bin/env python3
from asyncio import as_completed

from pathlib import Path
import translators as ts
from rich.progress import track
from attr import attrs, attrib

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

    async def run(
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

        await self.call_tts('title', self.reddit_object['thread_title'])
        async_tasks_offset = 1

        if self.reddit_object['thread_post'] and settings.config['settings']['storymode']:
            await self.call_tts('posttext', self.reddit_object['thread_post'])
            async_tasks_offset += 1

        async_tasks_primary = [
            self.call_tts(str(idx), comment['comment_body'])
            for idx, comment in enumerate(self.reddit_object['comments'])
        ]

        for task in track(
                as_completed(async_tasks_primary),
                description='Saving...',
                total=async_tasks_primary.__len__()
        ):
            await task

        print_substep('Saved Text to MP3 files successfully.', style='bold green')
        return [
            comments for comments, condition in
            zip(self.reddit_object['comments'], async_tasks_primary[async_tasks_offset:])
            if condition
        ]

    async def call_tts(
            self,
            filename: str,
            text: str
    ) -> bool:
        await self.tts_module.run(
            text=self.process_text(text),
            filepath=f'{self.path}/{filename}.mp3'
        )

        clip_length = audio_length(f'assets/audio/{filename}.mp3')

        if self.__total_length + clip_length <= self.max_length:
            self.max_length += clip_length
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
