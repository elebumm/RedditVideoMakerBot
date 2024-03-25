import random
import requests

from utils import settings


voices = ["Scarlett", "Amy", "Liv", "Dan", "Will"]

class UnrealSpeech:
    def __init__(self):
        self.url = "https://api.v6.unrealspeech.com/stream"
        self.max_chars = 120
        self.voices = voices

    def run(self, text, filepath, random_voice: bool = False):
        if settings.config["settings"]["tts"]["elevenlabs_api_key"]:
            api_key = settings.config["settings"]["tts"]["unreal_speech_api_key"]
        else:
            raise ValueError(
                "You didn't set an Unreal Speech API key! Please set the config variable UNREAL_SPEECH_API_KEY to a valid API key."
            )
        
        if random_voice:
            voice = self.randomvoice()
        else:
            if not settings.config["settings"]["tts"]["unreal_speech_voice_name"]:
                raise ValueError(
                    f"Please set the config variable UNREAL_SPEECH_VOICE_NAME to a valid voice. options are: {voices}"
                )
            voice = str(settings.config["settings"]["tts"]["unreal_speech_voice_name"]).capitalize()
        
        json = {
            'Text': text, # Up to 1000 characters
            'VoiceId': voice, # Dan, Will, Scarlett, Liv, Amy
            'Bitrate': '192k', # 320k, 256k, 192k, ...
            'Speed': '-0.15', # -1.0 to 1.0
            'Pitch': '1.2', # -0.5 to 1.5
            'Codec': 'libmp3lame', # libmp3lame or pcm_mulaw
        }
        headers = {'Authorization' : f'Bearer {api_key}'}
        response = requests.post(self.url, headers=headers, json=json)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)

    def randomvoice(self):
        return random.choice(self.voices)
