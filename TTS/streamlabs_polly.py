from aiohttp import ClientSession

from random import choice
from utils import settings
from attr import attrs, attrib
from attr.validators import instance_of

from TTS.common import BaseApiTTS, get_random_voice


voices = [
    'Brian',
    'Emma',
    'Russell',
    'Joey',
    'Matthew',
    'Joanna',
    'Kimberly',
    'Amy',
    'Geraint',
    'Nicole',
    'Justin',
    'Ivy',
    'Kendra',
    'Salli',
    'Raveena',
]


# valid voices https://lazypy.ro/tts/


@attrs(auto_attribs=True)
class StreamlabsPolly(BaseApiTTS):
    client: ClientSession = attrib(
        validator=instance_of(ClientSession),
    )
    random_voice: bool = False
    url: str = attrib(
        default='https://streamlabs.com/polly/speak',
        kw_only=True,
    )

    max_chars = 550

    async def make_request(
            self,
            text: str,
    ):
        voice = (
            get_random_voice(voices)
            if self.random_voice
            else str(settings.config['settings']['tts']['streamlabs_polly_voice']).capitalize()
            if str(settings.config['settings']['tts']['streamlabs_polly_voice']).lower() in [
                voice.lower() for voice in voices]
            else get_random_voice(voices)
        )

        async with self.client.post(
            self.url,
            data={
                'voice': voice,
                'text': text,
                'service': 'polly',
            }
        ) as response:
            speak_url = await(
                await response.json()
            )['speak_url']

        return await self.client.get(speak_url)
