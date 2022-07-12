import requests
from requests.exceptions import JSONDecodeError
from utils import settings
from attr import attrs, attrib

from TTS.common import BaseApiTTS, get_random_voice
from utils.voice import check_ratelimit

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
    random_voice: bool = False
    url: str = attrib(
        default='https://streamlabs.com/polly/speak',
        kw_only=True,
    )

    max_chars = 550

    def make_request(
            self,
            text,
    ):
        voice = (
            get_random_voice(voices)
            if self.random_voice
            else str(settings.config['settings']['tts']['streamlabs_polly_voice']).capitalize()
            if str(settings.config['settings']['tts']['streamlabs_polly_voice']).lower() in [
                voice.lower() for voice in voices]
            else get_random_voice(voices)
        )
        response = requests.post(
            self.url,
            data={
                'voice': voice,
                'text': text,
                'service': 'polly',
            })
        if not check_ratelimit(response):
            return self.make_request(text)
        else:
            try:
                results = requests.get(response.json()['speak_url'])
                return results
            except (KeyError, JSONDecodeError):
                try:
                    if response.json()['error'] == 'No text specified!':
                        raise ValueError('Please specify a text to convert to speech.')
                except (KeyError, JSONDecodeError):
                    print('Error occurred calling Streamlabs Polly')
