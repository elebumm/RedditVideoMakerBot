import os
import random

import requests

from utils import settings

MINIMAX_TTS_VOICES = [
    "English_Graceful_Lady",
    "English_Insightful_Speaker",
    "English_radiant_girl",
    "English_Persuasive_Man",
    "English_Lucky_Robot",
    "English_expressive_narrator",
]


class MiniMaxTTS:
    """
    A Text-to-Speech engine that uses the MiniMax TTS API to generate audio from text.

    Attributes:
        max_chars (int): Maximum number of characters allowed per API call.
        api_key (str): MiniMax API key loaded from settings or environment.
        base_url (str): The base URL for the MiniMax API.
        available_voices (list): Supported voice IDs.
    """

    def __init__(self):
        self.max_chars = 4096
        self.api_key = settings.config["settings"]["tts"].get("minimax_api_key") or os.environ.get(
            "MINIMAX_API_KEY"
        )
        if not self.api_key:
            raise ValueError(
                "No MiniMax API key provided! Set 'minimax_api_key' in your config or "
                "the MINIMAX_API_KEY environment variable."
            )
        self.base_url = settings.config["settings"]["tts"].get(
            "minimax_api_url", "https://api.minimax.io"
        ).rstrip("/")
        self.available_voices = MINIMAX_TTS_VOICES

    def randomvoice(self):
        """Return a random voice ID from the available voices."""
        return random.choice(self.available_voices)

    def run(self, text, filepath, random_voice: bool = False):
        """
        Convert the provided text to speech and save the resulting audio to the specified filepath.

        Args:
            text (str): The input text to convert.
            filepath (str): The file path where the generated audio will be saved.
            random_voice (bool): If True, select a random voice from the available voices.
        """
        if random_voice:
            voice = self.randomvoice()
        else:
            voice = settings.config["settings"]["tts"].get(
                "minimax_voice_name", "English_Graceful_Lady"
            )

        model = settings.config["settings"]["tts"].get("minimax_tts_model", "speech-2.8-hd")

        payload = {
            "model": model,
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice,
                "speed": 1,
                "vol": 1,
                "pitch": 0,
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1,
            },
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{self.base_url}/v1/t2a_v2",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"MiniMax TTS API error: {response.status_code} {response.text}"
            )

        result = response.json()
        if result.get("base_resp", {}).get("status_code") != 0:
            raise RuntimeError(
                f"MiniMax TTS API returned error: "
                f"{result.get('base_resp', {}).get('status_msg', 'Unknown error')}"
            )

        audio_hex = result["data"]["audio"]
        audio_bytes = bytes.fromhex(audio_hex)

        with open(filepath, "wb") as f:
            f.write(audio_bytes)
