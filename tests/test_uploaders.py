"""
Unit tests for uploaders — BaseUploader, YouTubeUploader, TikTokUploader,
FacebookUploader, and UploadManager.

All external API calls are mocked.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from uploaders.base_uploader import BaseUploader, VideoMetadata


# ===================================================================
# VideoMetadata
# ===================================================================


class TestVideoMetadata:
    def test_default_values(self):
        m = VideoMetadata(file_path="/tmp/video.mp4", title="Test")
        assert m.file_path == "/tmp/video.mp4"
        assert m.title == "Test"
        assert m.description == ""
        assert m.tags == []
        assert m.hashtags == []
        assert m.thumbnail_path is None
        assert m.schedule_time is None
        assert m.privacy == "public"
        assert m.category == "Entertainment"
        assert m.language == "vi"

    def test_custom_values(self):
        m = VideoMetadata(
            file_path="/tmp/video.mp4",
            title="Custom Video",
            description="Desc",
            tags=["tag1"],
            hashtags=["hash1"],
            privacy="private",
        )
        assert m.description == "Desc"
        assert m.tags == ["tag1"]
        assert m.privacy == "private"


# ===================================================================
# BaseUploader.validate_video
# ===================================================================


class TestBaseUploaderValidation:
    """Test validate_video on a concrete subclass."""

    def _make_uploader(self):
        class ConcreteUploader(BaseUploader):
            platform_name = "Test"

            def authenticate(self):
                return True

            def upload(self, metadata):
                return "https://example.com/video"

        return ConcreteUploader()

    def test_valid_video(self, sample_video_file):
        uploader = self._make_uploader()
        m = VideoMetadata(file_path=sample_video_file, title="Test Video")
        assert uploader.validate_video(m) is True

    def test_missing_file(self):
        uploader = self._make_uploader()
        m = VideoMetadata(file_path="/nonexistent/file.mp4", title="Test")
        assert uploader.validate_video(m) is False

    def test_empty_file(self, tmp_path):
        empty_file = tmp_path / "empty.mp4"
        empty_file.write_bytes(b"")
        uploader = self._make_uploader()
        m = VideoMetadata(file_path=str(empty_file), title="Test")
        assert uploader.validate_video(m) is False

    def test_missing_title(self, sample_video_file):
        uploader = self._make_uploader()
        m = VideoMetadata(file_path=sample_video_file, title="")
        assert uploader.validate_video(m) is False


# ===================================================================
# BaseUploader.safe_upload
# ===================================================================


class TestSafeUpload:
    def _make_uploader(self, upload_return=None, auth_return=True):
        class ConcreteUploader(BaseUploader):
            platform_name = "Test"

            def authenticate(self):
                self._authenticated = auth_return
                return auth_return

            def upload(self, metadata):
                return upload_return

        return ConcreteUploader()

    def test_successful_upload(self, sample_video_file):
        uploader = self._make_uploader(upload_return="https://example.com/v1")
        m = VideoMetadata(file_path=sample_video_file, title="Test Video")
        result = uploader.safe_upload(m, max_retries=1)
        assert result == "https://example.com/v1"

    def test_failed_auth(self, sample_video_file):
        uploader = self._make_uploader(auth_return=False)
        m = VideoMetadata(file_path=sample_video_file, title="Test Video")
        result = uploader.safe_upload(m, max_retries=1)
        assert result is None

    def test_retries_on_exception(self, sample_video_file):
        class FlakeyUploader(BaseUploader):
            platform_name = "Test"
            _call_count = 0

            def authenticate(self):
                self._authenticated = True
                return True

            def upload(self, metadata):
                self._call_count += 1
                if self._call_count < 3:
                    raise Exception("Temporary failure")
                return "https://example.com/v1"

        uploader = FlakeyUploader()
        m = VideoMetadata(file_path=sample_video_file, title="Test Video")
        with patch("time.sleep"):
            result = uploader.safe_upload(m, max_retries=3)
        assert result == "https://example.com/v1"

    def test_fails_after_max_retries(self, sample_video_file):
        class AlwaysFailUploader(BaseUploader):
            platform_name = "Test"

            def authenticate(self):
                self._authenticated = True
                return True

            def upload(self, metadata):
                raise Exception("Always fails")

        uploader = AlwaysFailUploader()
        m = VideoMetadata(file_path=sample_video_file, title="Test Video")
        with patch("time.sleep"):
            result = uploader.safe_upload(m, max_retries=2)
        assert result is None


# ===================================================================
# YouTubeUploader
# ===================================================================


class TestYouTubeUploader:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        mock_config["uploaders"]["youtube"]["enabled"] = True

    def test_authenticate_success(self):
        from uploaders.youtube_uploader import YouTubeUploader

        uploader = YouTubeUploader()
        with patch("uploaders.youtube_uploader.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"access_token": "yt_token_123"},
                raise_for_status=lambda: None,
            )
            assert uploader.authenticate() is True
            assert uploader.access_token == "yt_token_123"

    def test_authenticate_missing_creds(self, mock_config):
        mock_config["uploaders"]["youtube"]["client_id"] = ""
        from uploaders.youtube_uploader import YouTubeUploader

        uploader = YouTubeUploader()
        assert uploader.authenticate() is False

    def test_authenticate_api_error(self):
        from uploaders.youtube_uploader import YouTubeUploader

        uploader = YouTubeUploader()
        with patch("uploaders.youtube_uploader.requests.post") as mock_post:
            mock_post.side_effect = Exception("Auth failed")
            assert uploader.authenticate() is False

    def test_upload_returns_none_without_token(self, sample_video_file):
        from uploaders.youtube_uploader import YouTubeUploader

        uploader = YouTubeUploader()
        m = VideoMetadata(file_path=sample_video_file, title="Test")
        assert uploader.upload(m) is None

    def test_category_id_mapping(self):
        from uploaders.youtube_uploader import YouTubeUploader

        assert YouTubeUploader._get_category_id("Entertainment") == "24"
        assert YouTubeUploader._get_category_id("Gaming") == "20"
        assert YouTubeUploader._get_category_id("Unknown") == "24"

    def test_build_description(self):
        from uploaders.youtube_uploader import YouTubeUploader

        uploader = YouTubeUploader()
        m = VideoMetadata(
            file_path="/tmp/v.mp4",
            title="Test",
            description="Video description",
            hashtags=["trending", "viral"],
        )
        desc = uploader._build_description(m)
        assert "Video description" in desc
        assert "Threads Video Maker Bot" in desc


# ===================================================================
# TikTokUploader
# ===================================================================


class TestTikTokUploader:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        mock_config["uploaders"]["tiktok"]["enabled"] = True

    def test_authenticate_success(self):
        from uploaders.tiktok_uploader import TikTokUploader

        uploader = TikTokUploader()
        with patch("uploaders.tiktok_uploader.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"data": {"access_token": "tt_token_123"}},
                raise_for_status=lambda: None,
            )
            assert uploader.authenticate() is True
            assert uploader.access_token == "tt_token_123"

    def test_authenticate_no_token_in_response(self):
        from uploaders.tiktok_uploader import TikTokUploader

        uploader = TikTokUploader()
        with patch("uploaders.tiktok_uploader.requests.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"data": {}},
                raise_for_status=lambda: None,
            )
            assert uploader.authenticate() is False

    def test_privacy_mapping(self):
        from uploaders.tiktok_uploader import TikTokUploader

        assert TikTokUploader._map_privacy("public") == "PUBLIC_TO_EVERYONE"
        assert TikTokUploader._map_privacy("private") == "SELF_ONLY"
        assert TikTokUploader._map_privacy("friends") == "MUTUAL_FOLLOW_FRIENDS"
        assert TikTokUploader._map_privacy("unknown") == "PUBLIC_TO_EVERYONE"

    def test_build_caption(self):
        from uploaders.tiktok_uploader import TikTokUploader

        uploader = TikTokUploader()
        m = VideoMetadata(
            file_path="/tmp/v.mp4",
            title="Test Video Title",
            hashtags=["viral", "trending"],
        )
        caption = uploader._build_caption(m)
        assert "Test Video Title" in caption
        assert "#viral" in caption
        assert "#trending" in caption


# ===================================================================
# FacebookUploader
# ===================================================================


class TestFacebookUploader:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        mock_config["uploaders"]["facebook"]["enabled"] = True

    def test_authenticate_success(self):
        from uploaders.facebook_uploader import FacebookUploader

        uploader = FacebookUploader()
        with patch("uploaders.facebook_uploader.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": "page_123", "name": "Test Page"},
                raise_for_status=lambda: None,
            )
            assert uploader.authenticate() is True

    def test_authenticate_missing_token(self, mock_config):
        mock_config["uploaders"]["facebook"]["access_token"] = ""
        from uploaders.facebook_uploader import FacebookUploader

        uploader = FacebookUploader()
        assert uploader.authenticate() is False

    def test_authenticate_missing_page_id(self, mock_config):
        mock_config["uploaders"]["facebook"]["page_id"] = ""
        from uploaders.facebook_uploader import FacebookUploader

        uploader = FacebookUploader()
        assert uploader.authenticate() is False

    def test_build_description(self):
        from uploaders.facebook_uploader import FacebookUploader

        uploader = FacebookUploader()
        m = VideoMetadata(
            file_path="/tmp/v.mp4",
            title="Test",
            description="Some description",
            hashtags=["viral"],
        )
        desc = uploader._build_description(m)
        assert "Some description" in desc
        assert "#viral" in desc
        assert "Threads Video Maker Bot" in desc


# ===================================================================
# UploadManager
# ===================================================================


class TestUploadManager:
    def test_no_uploaders_when_disabled(self, mock_config):
        from uploaders.upload_manager import UploadManager

        manager = UploadManager()
        assert len(manager.uploaders) == 0

    def test_upload_to_all_empty(self, mock_config, sample_video_file):
        from uploaders.upload_manager import UploadManager

        manager = UploadManager()
        results = manager.upload_to_all(
            video_path=sample_video_file,
            title="Test",
        )
        assert results == {}

    def test_upload_to_platform_not_enabled(self, mock_config, sample_video_file):
        from uploaders.upload_manager import UploadManager

        manager = UploadManager()
        m = VideoMetadata(file_path=sample_video_file, title="Test")
        result = manager.upload_to_platform("youtube", m)
        assert result is None

    def test_default_hashtags(self):
        from uploaders.upload_manager import UploadManager

        hashtags = UploadManager._default_hashtags()
        assert "threads" in hashtags
        assert "viral" in hashtags
        assert "vietnam" in hashtags

    def test_init_with_enabled_uploaders(self, mock_config):
        mock_config["uploaders"]["youtube"]["enabled"] = True
        mock_config["uploaders"]["tiktok"]["enabled"] = True

        from uploaders.upload_manager import UploadManager

        manager = UploadManager()
        assert "youtube" in manager.uploaders
        assert "tiktok" in manager.uploaders
        assert "facebook" not in manager.uploaders

    def test_upload_to_all_with_mocked_uploaders(self, mock_config, sample_video_file):
        mock_config["uploaders"]["youtube"]["enabled"] = True

        from uploaders.upload_manager import UploadManager

        manager = UploadManager()

        # Mock the youtube uploader's safe_upload
        mock_uploader = MagicMock()
        mock_uploader.safe_upload.return_value = "https://youtube.com/watch?v=test"
        manager.uploaders["youtube"] = mock_uploader

        results = manager.upload_to_all(
            video_path=sample_video_file,
            title="Test Video",
            description="Test Description",
        )
        assert results["youtube"] == "https://youtube.com/watch?v=test"
