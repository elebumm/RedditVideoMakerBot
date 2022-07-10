from aiohttp import ClientSession

from utils import settings
from random import choice

from attr import attrs, attrib
from attr.validators import instance_of

from TTS.common import BaseApiTTS, get_random_voice

# TTS examples: https://twitter.com/scanlime/status/1512598559769702406

voices = dict()

voices['nonhuman'] = [  # DISNEY VOICES
    'en_us_ghostface',  # Ghost Face
    'en_us_chewbacca',  # Chewbacca
    'en_us_c3po',  # C3PO
    'en_us_stitch',  # Stitch
    'en_us_stormtrooper',  # Stormtrooper
    'en_us_rocket',  # Rocket
    # ENGLISH VOICES
]
voices['human'] = [
    'en_au_001',  # English AU - Female
    'en_au_002',  # English AU - Male
    'en_uk_001',  # English UK - Male 1
    'en_uk_003',  # English UK - Male 2
    'en_us_001',  # English US - Female (Int. 1)
    'en_us_002',  # English US - Female (Int. 2)
    'en_us_006',  # English US - Male 1
    'en_us_007',  # English US - Male 2
    'en_us_009',  # English US - Male 3
    'en_us_010',
]

voices['non_eng'] = [
    'fr_001',  # French - Male 1
    'fr_002',  # French - Male 2
    'de_001',  # German - Female
    'de_002',  # German - Male
    'es_002',  # Spanish - Male
    # AMERICA VOICES
    'es_mx_002',  # Spanish MX - Male
    'br_001',  # Portuguese BR - Female 1
    'br_003',  # Portuguese BR - Female 2
    'br_004',  # Portuguese BR - Female 3
    'br_005',  # Portuguese BR - Male
    # ASIA VOICES
    'id_001',  # Indonesian - Female
    'jp_001',  # Japanese - Female 1
    'jp_003',  # Japanese - Female 2
    'jp_005',  # Japanese - Female 3
    'jp_006',  # Japanese - Male
    'kr_002',  # Korean - Male 1
    'kr_003',  # Korean - Female
    'kr_004',  # Korean - Male 2
]


# good_voices: 'en_us_002', 'en_us_006'
# ok: 'en_au_002', 'en_uk_001'
# less: en_us_stormtrooper
# more or less: en_us_rocket, en_us_ghostface


@attrs(auto_attribs=True)
class TikTok(BaseApiTTS):  # TikTok Text-to-Speech Wrapper
    client: ClientSession = attrib(
        validator=instance_of(ClientSession),
    )
    random_voice: bool = False
    uri_base: str = attrib(
        default='https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke',
        kw_only=True,
    )
    max_chars = 300
    decode_base64 = True

    def __attrs_post_init__(self):
        self.voice = (
            get_random_voice(voices, 'human')
            if self.random_voice
            else str(settings.config['settings']['tts']['tiktok_voice']).lower()
            if str(settings.config['settings']['tts']['tiktok_voice']).lower() in [
                voice.lower() for dict_title in voices for voice in voices[dict_title]]
            else get_random_voice(voices, 'human')
        )

    async def make_request(
            self,
            text: str,
    ):
        return await self.client.post(
            f'{self.uri_base}',
            params={
                'text_speaker': self.voice,
                'req_text': text,
                'speaker_map_type': 0,
            }
        )
