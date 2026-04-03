import os
import tempfile
import pytest
from unittest.mock import patch, Mock, MagicMock


class TestCambAITTSUnit:
    """Unit tests for CambAITTS — all mocked, no API key needed."""

    def test_max_chars_is_5000(self):
        with patch("TTS.cambai.settings") as mock_settings:
            from TTS.cambai import CambAITTS
            tts = CambAITTS()
            assert tts.max_chars == 5000

    def test_initialize_raises_without_api_key(self):
        with patch("TTS.cambai.settings") as mock_settings:
            mock_settings.config = {"settings": {"tts": {"cambai_api_key": ""}}}
            from TTS.cambai import CambAITTS
            tts = CambAITTS()
            with pytest.raises(ValueError, match="CAMB AI API key"):
                tts.initialize()

    def test_initialize_creates_client(self):
        with patch("TTS.cambai.settings") as mock_settings, \
             patch("TTS.cambai.CambAI") as mock_camb:
            mock_settings.config = {"settings": {"tts": {"cambai_api_key": "test-key"}}}
            from TTS.cambai import CambAITTS
            tts = CambAITTS()
            tts.initialize()
            mock_camb.assert_called_once_with(api_key="test-key")
            assert tts.client is not None

    def test_run_generates_mp3(self):
        with patch("TTS.cambai.settings") as mock_settings, \
             patch("TTS.cambai.CambAI") as mock_camb_cls, \
             patch("TTS.cambai.save_stream_to_file") as mock_save, \
             patch("TTS.cambai.StreamTtsOutputConfiguration") as mock_config:
            mock_settings.config = {
                "settings": {"tts": {
                    "cambai_api_key": "test-key",
                    "cambai_voice_id": "147320",
                    "cambai_language": "en-us",
                    "cambai_speech_model": "mars-flash",
                }}
            }
            mock_client = Mock()
            mock_client.text_to_speech.tts.return_value = iter([b"fake-audio"])
            mock_camb_cls.return_value = mock_client

            from TTS.cambai import CambAITTS
            tts = CambAITTS()
            tts.run("Hello world", "/tmp/test.mp3", random_voice=False)

            mock_client.text_to_speech.tts.assert_called_once()
            call_kwargs = mock_client.text_to_speech.tts.call_args
            assert call_kwargs.kwargs["text"] == "Hello world"
            assert call_kwargs.kwargs["voice_id"] == 147320
            assert call_kwargs.kwargs["language"] == "en-us"
            assert call_kwargs.kwargs["speech_model"] == "mars-flash"
            mock_save.assert_called_once()
            assert mock_save.call_args[0][1] == "/tmp/test.mp3"

    def test_run_reads_config_voice_id(self):
        with patch("TTS.cambai.settings") as mock_settings, \
             patch("TTS.cambai.CambAI") as mock_camb_cls, \
             patch("TTS.cambai.save_stream_to_file"), \
             patch("TTS.cambai.StreamTtsOutputConfiguration"):
            mock_settings.config = {
                "settings": {"tts": {
                    "cambai_api_key": "test-key",
                    "cambai_voice_id": "99999",
                    "cambai_language": "es-es",
                    "cambai_speech_model": "mars-pro",
                }}
            }

            mock_client = Mock()
            mock_client.text_to_speech.tts.return_value = iter([b"audio"])
            mock_camb_cls.return_value = mock_client

            from TTS.cambai import CambAITTS
            tts = CambAITTS()
            tts.run("test", "/tmp/out.mp3")

            call_kwargs = mock_client.text_to_speech.tts.call_args.kwargs
            assert call_kwargs["voice_id"] == 99999
            assert call_kwargs["language"] == "es-es"
            assert call_kwargs["speech_model"] == "mars-pro"

    def test_random_voice_picks_from_list(self):
        with patch("TTS.cambai.settings") as mock_settings, \
             patch("TTS.cambai.CambAI") as mock_camb_cls, \
             patch("TTS.cambai.save_stream_to_file"), \
             patch("TTS.cambai.StreamTtsOutputConfiguration"), \
             patch("TTS.cambai.random") as mock_random:
            mock_settings.config = {"settings": {"tts": {"cambai_api_key": "test-key"}}}
            mock_client = Mock()
            mock_client.voice_cloning.list_voices.return_value = [
                {"id": 111, "voice_name": "Voice A"},
                {"id": 222, "voice_name": "Voice B"},
            ]
            mock_client.text_to_speech.tts.return_value = iter([b"audio"])
            mock_camb_cls.return_value = mock_client
            mock_random.choice.return_value = {"id": 222, "voice_name": "Voice B"}

            from TTS.cambai import CambAITTS
            tts = CambAITTS()
            tts.run("test", "/tmp/out.mp3", random_voice=True)

            mock_client.voice_cloning.list_voices.assert_called_once()
            mock_random.choice.assert_called_once()


@pytest.mark.integration
class TestCambAITTSIntegration:
    """Integration tests — require CAMB_API_KEY env var."""

    @pytest.fixture(autouse=True)
    def skip_without_key(self):
        if not os.environ.get("CAMB_API_KEY"):
            pytest.skip("CAMB_API_KEY not set")

    def test_real_api_generates_audio(self):
        from camb.client import CambAI, save_stream_to_file
        from camb.types import StreamTtsOutputConfiguration

        client = CambAI(api_key=os.environ["CAMB_API_KEY"])
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            filepath = f.name

        try:
            stream = client.text_to_speech.tts(
                text="Integration test for RedditVideoMakerBot.",
                language="en-us",
                voice_id=147320,
                speech_model="mars-flash",
                output_configuration=StreamTtsOutputConfiguration(format="mp3"),
            )
            save_stream_to_file(stream, filepath)
            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
