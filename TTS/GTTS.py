from gtts import gTTS


class GTTS:
    def tts(
        self,
        req_text: str = "Google Text To Speech",
        filename: str = "title.mp3",
        random_speaker=False,
        censor=False,
    ):
        tts = gTTS(text=req_text, lang="en", slow=False)
        tts.save(f"{filename}")
