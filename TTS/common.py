from aiofiles import open

import base64
from random import choice
from typing import Union, Optional


class BaseApiTTS:
    max_chars: int
    decode_base64: bool = False

    @staticmethod
    def text_len_sanitize(
            text: str,
            max_length: int,
    ) -> list:
        # Split by comma or dot (else you can lose intonations), if there is non, split by groups of 299 chars
        if '.' in text and all([split_text.__len__() < max_length for split_text in text.split('.')]):
            return text.split('.')

        if ',' in text and all([split_text.__len__() < max_length for split_text in text.split(',')]):
            return text.split(',')

        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

    async def write_file(
            self,
            output_text: str,
            filename: str,
    ) -> None:
        decoded_text = base64.b64decode(output_text) if self.decode_base64 else output_text

        async with open(filename, 'wb') as out:
            await out.write(decoded_text)

    async def run(
            self,
            req_text: str,
            filename: str,
    ) -> None:
        output_text = ''
        if len(req_text) > self.max_chars:
            for part in self.text_len_sanitize(req_text, self.max_chars):
                if part:
                    output_text += await self.make_request(part)
        else:
            output_text = await self.make_request(req_text)
        await self.write_file(output_text, filename)


def get_random_voice(
        voices: Union[list, dict],
        key: Optional[str] = None,
) -> str:
    if isinstance(voices, list):
        return choice(voices)
    else:
        return choice(voices[key])


def audio_length(
        path: str,
) -> float | int:
    from mutagen.mp3 import MP3

    try:
        audio = MP3(path)
        return audio.info.length
    except Exception as e:  # TODO add logging
        return 0
