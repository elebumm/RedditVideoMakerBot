"""Unit and integration tests for the MiniMax TTS provider."""
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers – fake out the settings module so we can import without a config file
# ---------------------------------------------------------------------------

FAKE_SETTINGS = {
    "settings": {
        "tts": {
            "minimax_api_key": "test-api-key",
            "minimax_api_url": "https://api.minimax.io",
            "minimax_voice_name": "English_Graceful_Lady",
            "minimax_tts_model": "speech-2.8-hd",
        }
    }
}


def _patch_settings(config=None):
    """Return a patcher that replaces utils.settings.config."""
    mock_settings = MagicMock()
    mock_settings.config = config or FAKE_SETTINGS
    return patch.dict("sys.modules", {"utils": MagicMock(settings=mock_settings)})


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


class TestMiniMaxTTSInit:
    """Provider instantiation and configuration parsing."""

    def test_creates_instance_with_valid_config(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            assert tts is not None

    def test_raises_when_api_key_missing(self):
        config = {"settings": {"tts": {}}}
        with _patch_settings(config), patch.dict(os.environ, {}, clear=False):
            # Make sure env var is absent too
            env = {k: v for k, v in os.environ.items() if k != "MINIMAX_API_KEY"}
            with patch.dict(os.environ, env, clear=True):
                from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

                with pytest.raises(ValueError, match="No MiniMax API key"):
                    MiniMaxTTS()

    def test_reads_api_key_from_env(self):
        config = {"settings": {"tts": {}}}
        with _patch_settings(config), patch.dict(os.environ, {"MINIMAX_API_KEY": "env-key"}):
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            assert tts.api_key == "env-key"

    def test_default_base_url(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            assert tts.base_url == "https://api.minimax.io"

    def test_available_voices_not_empty(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            assert len(tts.available_voices) > 0

    def test_max_chars(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            assert tts.max_chars == 4096


class TestMiniMaxTTSRandomVoice:
    def test_randomvoice_returns_valid_voice(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS, MINIMAX_TTS_VOICES  # noqa: PLC0415

            tts = MiniMaxTTS()
            voice = tts.randomvoice()
            assert voice in MINIMAX_TTS_VOICES


class TestMiniMaxTTSRun:
    """Tests for the run() method using a mocked requests.post."""

    def _make_mock_response(self, audio_hex="494433"):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {"audio": audio_hex, "status": 2},
            "base_resp": {"status_code": 0, "status_msg": "success"},
        }
        return mock_resp

    def test_sends_request_to_correct_url(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            with patch("requests.post", return_value=self._make_mock_response()) as mock_post:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tts.run("Hello world.", f.name)
                mock_post.assert_called_once()
                call_url = mock_post.call_args[0][0]
                assert "/v1/t2a_v2" in call_url
                assert "api.minimax.io" in call_url

    def test_sends_correct_payload(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            with patch("requests.post", return_value=self._make_mock_response()) as mock_post:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tts.run("Hello world.", f.name, random_voice=False)
                payload = mock_post.call_args[1]["json"]
                assert payload["model"] == "speech-2.8-hd"
                assert payload["text"] == "Hello world."
                assert payload["voice_setting"]["voice_id"] == "English_Graceful_Lady"
                assert payload["audio_setting"]["format"] == "mp3"

    def test_writes_audio_bytes_to_file(self):
        audio_hex = "494433"  # hex for 'ID3' — valid-ish mp3 header start
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            with patch("requests.post", return_value=self._make_mock_response(audio_hex)):
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tmp_path = f.name
                tts.run("Hello.", tmp_path)
                with open(tmp_path, "rb") as f:
                    content = f.read()
                assert content == bytes.fromhex(audio_hex)

    def test_raises_on_http_error(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_resp.text = "Unauthorized"
            with patch("requests.post", return_value=mock_resp):
                with pytest.raises(RuntimeError, match="MiniMax TTS API error: 401"):
                    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
                        tts.run("Hello.", f.name)

    def test_raises_on_api_status_error(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "data": {},
                "base_resp": {"status_code": 2013, "status_msg": "invalid voice_id"},
            }
            with patch("requests.post", return_value=mock_resp):
                with pytest.raises(RuntimeError, match="invalid voice_id"):
                    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
                        tts.run("Hello.", f.name)

    def test_uses_random_voice_when_requested(self):
        with _patch_settings():
            from TTS.minimax_tts import MiniMaxTTS, MINIMAX_TTS_VOICES  # noqa: PLC0415

            tts = MiniMaxTTS()
            captured_payloads = []

            def fake_post(url, **kwargs):
                captured_payloads.append(kwargs.get("json", {}))
                return self._make_mock_response()

            with patch("requests.post", side_effect=fake_post):
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tts.run("Hello.", f.name, random_voice=True)
            voice_used = captured_payloads[0]["voice_setting"]["voice_id"]
            assert voice_used in MINIMAX_TTS_VOICES


class TestTTSProvidersRegistry:
    """Verify MiniMax is registered in voices.py."""

    def test_minimax_in_providers_source(self):
        """Verify voices.py source contains MiniMax registration."""
        import pathlib

        voices_path = pathlib.Path(__file__).parent.parent / "video_creation" / "voices.py"
        source = voices_path.read_text()
        assert "MiniMax" in source, "MiniMax not found in TTSProviders registry"
        assert "MiniMaxTTS" in source, "MiniMaxTTS class not imported in voices.py"
        assert "minimax_tts" in source, "minimax_tts module not imported in voices.py"


# ---------------------------------------------------------------------------
# Integration test – calls the real MiniMax API (skipped if no key set)
# ---------------------------------------------------------------------------

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")


@pytest.mark.skipif(not MINIMAX_API_KEY, reason="MINIMAX_API_KEY not set")
class TestMiniMaxTTSIntegration:
    """Live API calls — only run when MINIMAX_API_KEY is available."""

    def test_synthesizes_speech_to_file(self):
        config = {
            "settings": {
                "tts": {
                    "minimax_api_key": MINIMAX_API_KEY,
                    "minimax_api_url": "https://api.minimax.io",
                    "minimax_voice_name": "English_Graceful_Lady",
                    "minimax_tts_model": "speech-2.8-hd",
                }
            }
        }
        with _patch_settings(config):
            from TTS.minimax_tts import MiniMaxTTS  # noqa: PLC0415

            tts = MiniMaxTTS()
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name
            tts.run("Hello, this is a MiniMax TTS test.", tmp_path)
            size = os.path.getsize(tmp_path)
            assert size > 100, f"Audio file too small ({size} bytes), likely empty or error"
            os.unlink(tmp_path)
