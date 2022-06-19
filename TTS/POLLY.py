import os
import random
import re

import requests
import sox
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from requests.exceptions import JSONDecodeError

voices = [
    "Brian",
    "Emma",
    "Russell",
    "Joey",
    "Matthew",
    "Joanna",
    "Kimberly",
    "Amy",
    "Geraint",
    "Nicole",
    "Justin",
    "Ivy",
    "Kendra",
    "Salli",
    "Raveena",
]


# valid voices https://lazypy.ro/tts/


class POLLY:
    def __init__(self):
        self.url = "https://streamlabs.com/polly/speak"

    def tts(
        self,
        req_text: str = "Amazon Text To Speech",
        filename: str = "title.mp3",
        random_speaker=False,
        censor=False,
    ):
        if random_speaker:
            voice = self.randomvoice()
        else:
            if not os.getenv("VOICE"):
                return ValueError(
                    "Please set the environment variable VOICE to a valid voice. options are: {}".format(
                        voices
                    )
                )
            voice = str(os.getenv("VOICE")).capitalize()
        body = {"voice": voice, "text": req_text, "service": "polly"}
        response = requests.post(self.url, data=body)
        try:
            voice_data = requests.get(response.json()["speak_url"])
            with open(filename, "wb") as f:
                f.write(voice_data.content)
        except (KeyError, JSONDecodeError):
            if response.json()["error"] == "Text length is too long!":
                chunks = [m.group().strip() for m in re.finditer(r" *((.{0,499})(\.|.$))", req_text)]

                audio_clips = []
                cbn = sox.Combiner()

                chunkId = 0
                for chunk in chunks:
                    body = {"voice": voice, "text": chunk, "service": "polly"}
                    resp = requests.post(self.url, data=body)
                    voice_data = requests.get(resp.json()["speak_url"])
                    with open(filename.replace(".mp3", f"-{chunkId}.mp3"), "wb") as out:
                        out.write(voice_data.content)

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

    def make_readable(self, text):
        """
        Amazon Polly fails to read some symbols properly such as '& (and)'.
        So we normalize input text before passing it to the service
        """
        text = text.replace("&", "and")
        return text

    def randomvoice(self):
        return random.choice(voices)
