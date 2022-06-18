import base64
import os
import random
import re

import requests
import sox
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from requests.adapters import HTTPAdapter, Retry

# from profanity_filter import ProfanityFilter
# pf = ProfanityFilter()
# Code by @JasonLovesDoggo
# https://twitter.com/scanlime/status/1512598559769702406

nonhuman = [  # DISNEY VOICES
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    # ENGLISH VOICES
]
human = [
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",
]
voices = nonhuman + human

noneng = [
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    # AMERICA VOICES
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # ASIA VOICES
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
]


# good_voices = {'good': ['en_us_002', 'en_us_006'],
#               'ok': ['en_au_002', 'en_uk_001']}  # less en_us_stormtrooper more less en_us_rocket en_us_ghostface


class TikTok:  # TikTok Text-to-Speech Wrapper
    def __init__(self):
        self.URI_BASE = (
            "https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/?text_speaker="
        )

    def tts(
        self,
        req_text: str = "TikTok Text To Speech",
        filename: str = "title.mp3",
        random_speaker: bool = False,
        censor=False,
    ):
        req_text = req_text.replace("+", "plus").replace(" ", "+").replace("&", "and")
        if censor:
            # req_text = pf.censor(req_text)
            pass
        voice = (
            self.randomvoice() if random_speaker else (os.getenv("VOICE") or random.choice(human))
        )

        chunks = [m.group().strip() for m in re.finditer(r" *((.{0,299})(\.|.$))", req_text)]

        audio_clips = []
        cbn = sox.Combiner()
        # cbn.set_input_format(file_type=["mp3" for _ in chunks])

        chunkId = 0
        for chunk in chunks:
            try:
                r = requests.post(f"{self.URI_BASE}{voice}&req_text={chunk}&speaker_map_type=0")
            except requests.exceptions.SSLError:
                # https://stackoverflow.com/a/47475019/18516611
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                r = session.post(f"{self.URI_BASE}{voice}&req_text={chunk}&speaker_map_type=0")
            print(r.text)
            vstr = [r.json()["data"]["v_str"]][0]
            b64d = base64.b64decode(vstr)

            with open(filename.replace(".mp3", f"-{chunkId}.mp3"), "wb") as out:
                out.write(b64d)

            audio_clips.append(filename.replace(".mp3", f"-{chunkId}.mp3"))

            chunkId = chunkId + 1
        try:
            if len(audio_clips) > 1:
                cbn.convert(samplerate=44100, n_channels=2)
                cbn.build(audio_clips, filename, "concatenate")
            else:
                os.rename(audio_clips[0], filename)
        except (
            sox.core.SoxError,
            FileNotFoundError,
        ):  # https://github.com/JasonLovesDoggo/RedditVideoMakerBot/issues/67#issuecomment-1150466339
            for clip in audio_clips:
                i = audio_clips.index(clip)  # get the index of the clip
                audio_clips = (
                    audio_clips[:i] + [AudioFileClip(clip)] + audio_clips[i + 1 :]
                )  # replace the clip with an AudioFileClip
            audio_concat = concatenate_audioclips(audio_clips)
            audio_composite = CompositeAudioClip([audio_concat])
            audio_composite.write_audiofile(filename, 44100, 2, 2000, None)

    @staticmethod
    def randomvoice():
        ok_or_good = random.randrange(1, 10)
        if ok_or_good == 1:  # 1/10 chance of ok voice
            return random.choice(voices)
        return random.choice(human)  # 9/10 chance of good voice
