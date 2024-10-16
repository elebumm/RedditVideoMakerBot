import os
import io
import random
from pydub import AudioSegment
from pydub.playback import play
import azure.cognitiveservices.speech as speechsdk
from utils import settings


class AzureTTS:
    def __init__(self):
        self.voices = []
        self.api_key = settings.config["settings"]["tts"]["azure_api_key"]
        self.region = settings.config["settings"]["tts"]["azure_region"]
        self.default_voice = settings.config["settings"]["tts"]["azure_voice_name"]
        self.rate = settings.config["settings"]["tts"]["azure_voice_speed_boost"]

    def run(self, text: str, filepath: str, random_voice=False):
        if not self.api_key or not self.region:
            raise ValueError("Azure API key and region must be set in settings.")

        if not isinstance(self.rate, int) or not (0 <= self.rate <= 100):
            raise ValueError(
                "azure_voice_speed_boost must be an integer between 0 and 100."
            )

        speech_config = speechsdk.SpeechConfig(
            subscription=self.api_key, region=self.region
        )
        audio_config = speechsdk.audio.AudioOutputConfig(filename=filepath)

        if random_voice:
            voice_name = self.random_voice()
        else:
            voice_name = self.default_voice

        speech_config.speech_synthesis_voice_name = voice_name
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )
        rate_with_percent = f"{self.rate}%"

        # Construct SSML with the specified rate
        ssml_text = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{voice_name}">
                <prosody rate="{rate_with_percent}">{text}</prosody>
            </voice>
        </speak>
        """
        result = speech_synthesizer.speak_ssml_async(ssml_text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized for text [{text}] and saved to [{filepath}]")
        else:
            print(f"Speech synthesis failed: {result.reason}")

    def random_voice(self):
        if not self.voices:
            self.voices = self.fetch_available_voices()
        return random.choice(self.voices)

    def fetch_available_voices(self):
        return [
            "en-US-AndrewMultilingualNeural",
            "en-US-AvaMultilingualNeural",
            "de-DE-FlorianMultilingualNeural",
            "en-US-EmmaMultilingualNeural",
            "de-DE-SeraphinaMultilingualNeural",
            "de-DE-FlorianMultilingualNeural",
            "fr-FR-VivienneMultilingualNeural",
            "fr-FR-RemyMultilingualNeural",
            "zh-CN-XiaoxiaoMultilingualNeural",
            "zh-CN-XiaochenMultilingualNeural",
            "zh-CN-XiaoyuMultilingualNeural",
            "zh-CN-YunyiMultilingualNeural",
        ]
