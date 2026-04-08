"""
Unit tests for TTS modules — GTTS and TTSEngine.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


# Pre-mock heavy dependencies that may not be installed in test env
@pytest.fixture(autouse=True)
def _mock_tts_deps(monkeypatch):
    """Mock heavy TTS dependencies."""
    # Mock gtts
    mock_gtts_module = MagicMock()
    mock_gtts_class = MagicMock()
    mock_gtts_module.gTTS = mock_gtts_class
    monkeypatch.setitem(sys.modules, "gtts", mock_gtts_module)

    # Mock numpy
    monkeypatch.setitem(sys.modules, "numpy", MagicMock())

    # Mock translators
    monkeypatch.setitem(sys.modules, "translators", MagicMock())

    # Mock moviepy and submodules
    mock_moviepy = MagicMock()
    monkeypatch.setitem(sys.modules, "moviepy", mock_moviepy)
    monkeypatch.setitem(sys.modules, "moviepy.audio", MagicMock())
    monkeypatch.setitem(sys.modules, "moviepy.audio.AudioClip", MagicMock())
    monkeypatch.setitem(sys.modules, "moviepy.audio.fx", MagicMock())

    # Clear cached imports to force reimport with mocks
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("TTS."):
            del sys.modules[mod_name]


# ===================================================================
# GTTS
# ===================================================================


class TestGTTS:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        pass

    def test_init(self):
        from TTS.GTTS import GTTS

        engine = GTTS()
        assert engine.max_chars == 5000
        assert engine.voices == []

    def test_run_saves_file(self, tmp_path):
        from TTS.GTTS import GTTS

        engine = GTTS()
        filepath = str(tmp_path / "test.mp3")

        with patch("TTS.GTTS.gTTS") as MockGTTS:
            mock_tts_instance = MagicMock()
            MockGTTS.return_value = mock_tts_instance

            engine.run("Hello world", filepath)

            MockGTTS.assert_called_once_with(text="Hello world", lang="vi", slow=False)
            mock_tts_instance.save.assert_called_once_with(filepath)

    def test_run_uses_config_lang(self, mock_config):
        from TTS.GTTS import GTTS

        mock_config["threads"]["thread"]["post_lang"] = "en"
        engine = GTTS()

        with patch("TTS.GTTS.gTTS") as MockGTTS:
            MockGTTS.return_value = MagicMock()
            engine.run("test", "/tmp/test.mp3")
            MockGTTS.assert_called_once_with(text="test", lang="en", slow=False)

    def test_randomvoice_returns_from_list(self):
        from TTS.GTTS import GTTS

        engine = GTTS()
        engine.voices = ["voice1", "voice2", "voice3"]
        voice = engine.randomvoice()
        assert voice in engine.voices


# ===================================================================
# TTSEngine
# ===================================================================


class TestTTSEngine:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        pass

    def test_init_creates_paths(self, sample_thread_object):
        from TTS.engine_wrapper import TTSEngine

        mock_module = MagicMock
        engine = TTSEngine(
            tts_module=mock_module,
            reddit_object=sample_thread_object,
            path="assets/temp/",
            max_length=50,
        )
        assert engine.redditid == "test_thread_123"
        assert "test_thread_123/mp3" in engine.path

    def test_add_periods_removes_urls(self, sample_thread_object):
        from TTS.engine_wrapper import TTSEngine

        sample_thread_object["comments"] = [
            {
                "comment_body": "Check https://example.com and more\nAnother line",
                "comment_id": "c1",
                "comment_url": "",
                "comment_author": "@user",
            }
        ]

        mock_module = MagicMock
        engine = TTSEngine(
            tts_module=mock_module,
            reddit_object=sample_thread_object,
            path="assets/temp/",
        )
        engine.add_periods()
        body = sample_thread_object["comments"][0]["comment_body"]
        assert "https://" not in body
        # Newlines should be replaced with ". "
        assert "\n" not in body
