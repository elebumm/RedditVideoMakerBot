def audio_length(
        path: str,
) -> float | int:
    from mutagen.mp3 import MP3

    try:
        audio = MP3(path)
        return audio.info.length
    except Exception as e:  # TODO add logging
        return 0
