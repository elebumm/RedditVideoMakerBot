import random

from elevenlabs import save, Voice
from elevenlabs.client import ElevenLabs

from utils import settings


class elevenlabs:
    def __init__(self):
        self.max_chars = 2500
        self.client: ElevenLabs = None
        self.available_voices: list[Voice] = []  # To store fetched voices

    @staticmethod
    def get_available_voices(api_key: str) -> list[str]:
        """
        Fetches available voice names from ElevenLabs using a given API key.
        Returns a list of voice names, or an empty list on failure.
        """
        if not api_key:
            return []
        try:
            client = ElevenLabs(api_key=api_key)
            voices = client.voices.get_all().voices
            return sorted([voice.name for voice in voices])
        except Exception:
            # Fail silently and return an empty list. The caller will handle the message.
            return []

    def run(self, text, filepath, random_voice: bool = False):
        if self.client is None:
            self.initialize()

        voice_id_to_use = None
        if random_voice:
            voice_id_to_use = self.randomvoice()
        else:
            configured_voice_name = str(settings.config["settings"]["tts"]["elevenlabs_voice_name"]).strip()
            if not configured_voice_name:  # If name is blank, use random
                voice_id_to_use = self.randomvoice()
            else:
                # Look up the configured voice name in the cached available voices
                for voice_obj in self.available_voices:
                    if voice_obj.name.lower() == configured_voice_name.lower():
                        voice_id_to_use = voice_obj.voice_id
                        break

                if voice_id_to_use is None:
                    # Provide a helpful error message if the configured voice is not found
                    available_voice_names = [v.name for v in self.available_voices]
                    raise ValueError(
                        f"Configured ElevenLabs voice '{configured_voice_name}' not found. "
                        f"Available voices for your account are: {', '.join(available_voice_names)}. "
                        "Please update 'elevenlabs_voice_name' in your config.toml or GUI."
                    )

        audio = self.client.text_to_speech.convert(
            text=text, voice_id=voice_id_to_use, model_id="eleven_multilingual_v2"
        )
        save(audio=audio, filename=filepath)

    def initialize(self):
        api_key = settings.config["settings"]["tts"].get("elevenlabs_api_key")
        if not api_key:
            raise ValueError(
                "You didn't set an Elevenlabs API key! Please set the config variable ELEVENLABS_API_KEY to a valid API key."
            )

        self.client = ElevenLabs(api_key=api_key)
        # Fetch and store available voices during initialization
        try:
            self.available_voices = self.client.voices.get_all().voices
            if not self.available_voices:
                raise RuntimeError("No voices found for your ElevenLabs account. Please check your API key and account status.")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch ElevenLabs voices: {e}. Please check your API key and internet connection.")

    def randomvoice(self):
        if self.client is None:
            self.initialize()
        if not self.available_voices:
            raise RuntimeError("No voices available from ElevenLabs account to choose from.")
        # Return the voice_id of a randomly selected voice object
        return random.choice(self.available_voices).voice_id
