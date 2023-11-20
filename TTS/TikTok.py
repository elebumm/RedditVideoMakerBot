# documentation for tiktok api: https://github.com/oscie57/tiktok-voice/wiki

import base64
import random
import time
from typing import Optional, Final
import requests

from utils import settings

__all__ = ["TikTok", "TikTokTTSException"]

disney_voices: Final[tuple] = (
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    "en_female_madam_leota",  # Madame Leota
    "en_male_ghosthost",  # Ghost Host
    "en_male_pirate",  # pirate
)

eng_voices: Final[tuple] = (
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",  # English US - Male 4
    "en_male_narration",  # Narrator
    "en_female_emotional",  # Peaceful
    "en_male_cody",  # Serious
)

non_eng_voices: Final[tuple] = (
    # Western European voices
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    "it_male_m18",  # Italian - Male
    # South american voices
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # asian voices
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
)

vocals: Final[tuple] = (
    "en_female_f08_salut_damour",  # Alto
    "en_male_m03_lobby",  # Tenor
    "en_male_m03_sunshine_soon",  # Sunshine Soon
    "en_female_f08_warmy_breeze",  # Warmy Breeze
    "en_female_ht_f08_glorious",  # Glorious
    "en_male_sing_funny_it_goes_up",  # It Goes Up
    "en_male_m2_xhxs_m03_silly",  # Chipmunk
    "en_female_ht_f08_wonderful_world",  # Dramatic
)


class TikTok:
    """TikTok Text-to-Speech Wrapper"""

    def __init__(self):
        headers = {
            "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; "
            "Build/NRD90M;tt-ok/3.12.13.1)",
            "Cookie": f"sessionid={settings.config['settings']['tts']['tiktok_sessionid']}",
        }

        self.URI_BASE = (
            "https://tiktok-tts.weilnet.workers.dev/api/generation"
        )
        self.max_chars = 200

        self._session = requests.Session()
        # set the headers to the session, so we don't have to do it for every request
        self._session.headers = headers

    def run(self, text: str, filepath: str, random_voice: bool = False):
        if random_voice:
            voice = self.random_voice()
        else:
            # if tiktok_voice is not set in the config file, then use a random voice
            voice = settings.config["settings"]["tts"].get("tiktok_voice", None)

        # get the audio from the TikTok API
        data = self.get_voices(voice=voice, text=text)
        # check if there was an error in the request
        status_code = data["error"]

        # decode data from base64 to binary
        try:
            raw_voices = data["data"]
        except:
            print(
                "The TikTok TTS returned an invalid response. Please try again later, and report this bug."
            )
            raise TikTokTTSException(0, "Invalid response")
        decoded_voices = base64.b64decode(raw_voices)

        # write voices to specified filepath
        with open(filepath, "wb") as out:
            out.write(decoded_voices)

    def get_voices(self, text: str, voice: Optional[str] = None) -> dict:
        """If voice is not passed, the API will try to use the most fitting voice"""
        # sanitize text
        text = text.replace("+", "plus").replace("&", "and").replace("r/", "")

        # prepare url request
        params = {"text": text,"voice": voice}
        if voice is not None:
            params["voice"] = voice

        # send request
        try:
            response = self._session.post(self.URI_BASE, json=params)
        except ConnectionError:
            time.sleep(random.randrange(1, 7))
            response = self._session.post(self.URI_BASE, json=params)

        return response.json()

    @staticmethod
    def random_voice() -> str:
        return random.choice(eng_voices)


class TikTokTTSException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Code: {self.status_code}, Message: {self.message}"
