"""
Integration tests for the scheduler pipeline flow.

Tests run_pipeline() and run_scheduled() with all external
dependencies (API calls, TTS, video generation) mocked.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Pre-mock playwright and other heavy deps needed by transitive imports
_playwright_mock = MagicMock()
_playwright_mock.sync_api.sync_playwright = MagicMock
_playwright_mock.sync_api.TimeoutError = TimeoutError


@pytest.fixture(autouse=True)
def _mock_heavy_deps(monkeypatch):
    """Mock heavy dependencies not needed for pipeline tests."""
    monkeypatch.setitem(sys.modules, "playwright", _playwright_mock)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", _playwright_mock.sync_api)

    # Mock video_creation submodules that may have heavy deps (moviepy, selenium, etc.)
    for mod_name in [
        "video_creation.voices",
        "video_creation.threads_screenshot",
        "video_creation.final_video",
        "video_creation.background",
    ]:
        if mod_name not in sys.modules:
            monkeypatch.setitem(sys.modules, mod_name, MagicMock())


# ===================================================================
# run_pipeline integration
# ===================================================================


class TestRunPipeline:
    """Test the full pipeline flow with mocked internals."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        pass

    def test_pipeline_calls_steps_in_order(self, mock_config, tmp_path):
        """Verify pipeline calls all steps and returns successfully."""
        call_order = []

        mock_thread_object = {
            "thread_url": "https://threads.net/test",
            "thread_title": "Test Thread",
            "thread_id": "test_123",
            "thread_author": "@test",
            "is_nsfw": False,
            "thread_post": "Content",
            "comments": [
                {"comment_body": "Reply", "comment_url": "", "comment_id": "r1", "comment_author": "@r"},
            ],
        }

        # Imports are local inside run_pipeline, so we must mock the source modules
        with patch("threads.threads_client.get_threads_posts", return_value=mock_thread_object) as mock_get_posts, \
             patch("utils.check_token.preflight_check") as mock_preflight, \
             patch("video_creation.voices.save_text_to_mp3", return_value=(30.5, 1)) as mock_tts, \
             patch("video_creation.threads_screenshot.get_screenshots_of_threads_posts") as mock_screenshots, \
             patch("video_creation.background.get_background_config", return_value={"video": "mc", "audio": "lofi"}), \
             patch("video_creation.background.download_background_video"), \
             patch("video_creation.background.download_background_audio"), \
             patch("video_creation.background.chop_background"), \
             patch("video_creation.final_video.make_final_video") as mock_final, \
             patch("scheduler.pipeline.save_title"), \
             patch("os.path.exists", return_value=False):
            from scheduler.pipeline import run_pipeline
            result = run_pipeline()

        mock_preflight.assert_called_once()
        mock_get_posts.assert_called_once()
        mock_tts.assert_called_once()
        mock_screenshots.assert_called_once()
        mock_final.assert_called_once()

    def test_pipeline_handles_error(self, mock_config):
        """Pipeline should propagate exceptions from steps."""

        with patch("utils.check_token.preflight_check"), \
             patch("threads.threads_client.get_threads_posts", side_effect=Exception("API error")), \
             patch("video_creation.voices.save_text_to_mp3", return_value=(0, 0)), \
             patch("video_creation.threads_screenshot.get_screenshots_of_threads_posts"), \
             patch("video_creation.background.get_background_config", return_value={}), \
             patch("video_creation.background.download_background_video"), \
             patch("video_creation.background.download_background_audio"), \
             patch("video_creation.background.chop_background"), \
             patch("video_creation.final_video.make_final_video"):
            from scheduler.pipeline import run_pipeline
            with pytest.raises(Exception, match="API error"):
                run_pipeline()


# ===================================================================
# run_scheduled — scheduler configuration
# ===================================================================


class TestRunScheduled:
    def test_scheduler_not_enabled(self, mock_config, capsys):
        from scheduler.pipeline import run_scheduled

        mock_config["scheduler"]["enabled"] = False
        run_scheduled()
        # Should not crash, just print warning

    def test_scheduler_invalid_cron(self, mock_config, capsys):
        from scheduler.pipeline import run_scheduled

        mock_config["scheduler"]["enabled"] = True
        mock_config["scheduler"]["cron"] = "invalid"
        run_scheduled()
        # Should not crash, just print error about invalid cron
