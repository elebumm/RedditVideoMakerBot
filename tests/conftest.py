"""
Shared fixtures for the test suite.

Provides mock configurations, temporary directories, and common test data
used across all test modules.
"""

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Mock configuration dictionary matching the project's config.toml structure
# ---------------------------------------------------------------------------

MOCK_CONFIG = {
    "threads": {
        "creds": {
            "access_token": "FAKE_ACCESS_TOKEN_FOR_TESTING",
            "user_id": "123456789",
        },
        "thread": {
            "source": "user",
            "target_user_id": "",
            "post_id": "",
            "keywords": "",
            "max_comment_length": 500,
            "min_comment_length": 1,
            "post_lang": "vi",
            "min_comments": 0,
            "blocked_words": "",
            "channel_name": "test_channel",
            "use_conversation": True,
            "use_insights": True,
            "search_query": "",
            "search_type": "TOP",
            "search_mode": "KEYWORD",
            "search_media_type": "",
        },
        "publishing": {
            "enabled": False,
            "reply_control": "everyone",
            "check_quota": True,
        },
    },
    "reddit": {
        "creds": {
            "client_id": "",
            "client_secret": "",
            "username": "",
            "password": "",
            "2fa": False,
        },
        "thread": {
            "subreddit": "AskReddit",
            "post_id": "",
            "post_lang": "en",
        },
    },
    "settings": {
        "allow_nsfw": False,
        "theme": "dark",
        "times_to_run": 1,
        "opacity": 0.9,
        "storymode": False,
        "storymode_method": 0,
        "resolution_w": 1080,
        "resolution_h": 1920,
        "zoom": 1.0,
        "channel_name": "test",
        "background": {
            "background_video": "minecraft-parkour-1",
            "background_audio": "lofi-1",
            "background_audio_volume": 0.15,
            "enable_extra_audio": False,
            "background_thumbnail": True,
            "background_thumbnail_font_family": "arial",
            "background_thumbnail_font_size": 36,
            "background_thumbnail_font_color": "255,255,255",
        },
        "tts": {
            "voice_choice": "GoogleTranslate",
            "random_voice": False,
            "no_emojis": True,
            "elevenlabs_voice_name": "Rachel",
            "elevenlabs_api_key": "",
            "aws_polly_voice": "Joanna",
            "tiktok_voice": "en_us_001",
            "tiktok_sessionid": "",
            "python_voice": "0",
            "openai_api_key": "",
            "openai_voice_name": "alloy",
            "openai_model": "tts-1",
        },
    },
    "uploaders": {
        "youtube": {
            "enabled": False,
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "tiktok": {
            "enabled": False,
            "client_key": "test_client_key",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
        "facebook": {
            "enabled": False,
            "access_token": "test_access_token",
            "page_id": "test_page_id",
        },
    },
    "scheduler": {
        "enabled": False,
        "cron": "0 */3 * * *",
        "timezone": "Asia/Ho_Chi_Minh",
        "max_videos_per_day": 8,
    },
}


@pytest.fixture
def mock_config(monkeypatch):
    """Inject a mock configuration into ``utils.settings.config``."""
    import copy

    import utils.settings as _settings

    cfg = copy.deepcopy(MOCK_CONFIG)
    monkeypatch.setattr(_settings, "config", cfg)
    return cfg


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory for test file I/O."""
    return tmp_path


@pytest.fixture
def sample_thread_object():
    """Return a representative Threads content object used throughout the pipeline."""
    return {
        "thread_url": "https://www.threads.net/@user/post/ABC123",
        "thread_title": "Test Thread Title for Video",
        "thread_id": "test_thread_123",
        "thread_author": "@test_user",
        "is_nsfw": False,
        "thread_post": "This is the main thread post content for testing.",
        "comments": [
            {
                "comment_body": "First test comment reply.",
                "comment_url": "https://www.threads.net/@user/post/ABC123/reply1",
                "comment_id": "reply_001",
                "comment_author": "@commenter_1",
            },
            {
                "comment_body": "Second test comment reply with more text.",
                "comment_url": "https://www.threads.net/@user/post/ABC123/reply2",
                "comment_id": "reply_002",
                "comment_author": "@commenter_2",
            },
        ],
    }


@pytest.fixture
def sample_video_file(tmp_path):
    """Create a minimal fake video file for upload tests."""
    video = tmp_path / "test_video.mp4"
    video.write_bytes(b"\x00" * 1024)  # 1KB dummy file
    return str(video)


@pytest.fixture
def sample_thumbnail_file(tmp_path):
    """Create a minimal fake thumbnail file."""
    thumb = tmp_path / "thumbnail.png"
    thumb.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    return str(thumb)


@pytest.fixture
def title_history_file(tmp_path):
    """Create a temporary title history JSON file."""
    history_file = tmp_path / "title_history.json"
    history_file.write_text("[]", encoding="utf-8")
    return str(history_file)


@pytest.fixture
def videos_json_file(tmp_path):
    """Create a temporary videos.json file."""
    videos_file = tmp_path / "videos.json"
    videos_file.write_text("[]", encoding="utf-8")
    return str(videos_file)
