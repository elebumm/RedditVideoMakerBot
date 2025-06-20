import random

from elevenlabs import Voice
from elevenlabs.client import ElevenLabs

from utils import settings


class elevenlabs:
    def __init__(self):
        self.max_chars = 2500
        self.client: ElevenLabs = None
        self.available_voices: list[Voice] = []  # To store fetched Voice objects
        self.voice_name_to_id_map: dict[str, str] = {} # To store name -> id mapping for quick lookup

    @staticmethod
    def get_available_voices(api_key: str) -> dict[str, str]:
        """
        Fetches available voice names and their IDs from ElevenLabs using a given API key.
        Returns a dictionary mapping voice names (lowercase) to voice IDs, or an empty dict on failure.
        """
        if not api_key:
            return {}
        try:
            client = ElevenLabs(api_key=api_key)
            print("\n[1/4] Fetching available ElevenLabs voices...")
            # Keep client.voices.search as per original code and potential test dependency.
            # The search method returns GetVoicesV2Response which has a 'voices' attribute.
            response = client.voices.search(include_total_count=True, page_size=100) #page-size specified as endpoint returns paginated data
            if not response.voices:
                    raise RuntimeError("No voices found for your ElevenLabs account. Please check your API key.")
            voice_mapping = {voice.name.lower(): voice.voice_id for voice in response.voices}
            print(f"✅ Success! Found {response.total_count} voices for your account:")
            return voice_mapping
        except Exception as e:
                    print(f"❌ Failed to fetch ElevenLabs voices: {e}")
                    return {}

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
                # Use the pre-built map for efficient lookup
                voice_id_to_use = self.voice_name_to_id_map.get(configured_voice_name.lower())

                if voice_id_to_use is None:
                    # Provide a helpful error message if the configured voice is not found
                    available_voice_names = list(self.voice_name_to_id_map.keys()) # Get names from the map
                    raise ValueError(
                        f"Configured ElevenLabs voice '{configured_voice_name}' not found. "
                        f"Available voices for your account are: {', '.join(available_voice_names)}. "
                        "Please update 'elevenlabs_voice_name' in your config.toml or GUI."
                    )

        audio_stream = self.client.text_to_speech.convert(
            text=text, voice_id=voice_id_to_use, model_id="eleven_multilingual_v2"
        )
        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

    def initialize(self):
        api_key = settings.config["settings"]["tts"].get("elevenlabs_api_key")
        if not api_key:
            raise ValueError(
                "You didn't set an Elevenlabs API key! Please set the config variable ELEVENLABS_API_KEY to a valid API key."
            )

        self.client = ElevenLabs(api_key=api_key)
        # Fetch and store available voices during initialization
        try:
            self.available_voices = self.client.voices.get_all().voices # Store Voice objects
            self.voice_name_to_id_map = {voice.name.lower(): voice.voice_id for voice in self.available_voices} # Build the map
            if not self.available_voices:
                raise RuntimeError("No voices found for your ElevenLabs account. Please check your API key and account status.")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch ElevenLabs voices: {e}. Please check your API key and internet connection.")

    def randomvoice(self):
        if self.client is None:
            self.initialize()
        if not self.available_voices: # Use the list of Voice objects
            raise RuntimeError("No voices available from ElevenLabs account to choose from.")
        # Return the voice_id of a randomly selected voice object
        return random.choice(self.available_voices).voice_id
