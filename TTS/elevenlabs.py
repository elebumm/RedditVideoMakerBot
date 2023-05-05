import random

from elevenlabs import generate, save

from utils import settings


class elevenlabs:
    def __init__(self):
        self.max_chars = 5000
        self.voices = ["Adam", "Antoni", "Arnold", "Bella", "Domi", "Elli", "Josh", "Rachel", "Sam"]

    def run(
        self,
        text: str,
        filepath: str,
        random_voice=False,
    ):
        voice_name = settings.config["settings"]["tts"]["elevenlabs_voice_name"]
        if voice_name == "":
            voice_name = "Bella"
            raise ValueError(
                "set elevenlabs name value to a valid value, switching to default voice (Bella)"
            )
        if random_voice:
            voice_name = self.randomvoice()

        if settings.config["settings"]["tts"]["elevenlabs_api_key"]:
            api_key = settings.config["settings"]["tts"]["elevenlabs_api_key"]
        else:
            api_key = None
            print("set elevenlabs api key value to a valid value or quota will be limited")
        
        audio = generate(
            api_key=api_key,
            text=text,
            voice=voice_name,
            model="eleven_monolingual_v1"
        )
        save(
            audio=audio,         
            filename=f"{filepath}"
        )

    def randomvoice(self):
        return random.choice(self.voices)
