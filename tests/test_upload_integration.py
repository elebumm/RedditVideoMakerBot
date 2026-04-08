"""
Integration tests for upload pipeline — verifying the UploadManager
orchestrates multi-platform uploads correctly with mocked external APIs.
"""

from unittest.mock import MagicMock, patch

import pytest

from uploaders.base_uploader import VideoMetadata


# ===================================================================
# Full upload pipeline integration
# ===================================================================


class TestUploadPipelineIntegration:
    """Test the full upload_to_all flow with all platforms enabled."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config, sample_video_file):
        self.video_path = sample_video_file
        # Enable all uploaders
        mock_config["uploaders"]["youtube"]["enabled"] = True
        mock_config["uploaders"]["tiktok"]["enabled"] = True
        mock_config["uploaders"]["facebook"]["enabled"] = True

    def test_all_platforms_succeed(self, mock_config):
        from uploaders.upload_manager import UploadManager

        manager = UploadManager()

        # Replace all uploaders with mocks
        for platform in manager.uploaders:
            mock_up = MagicMock()
            mock_up.safe_upload.return_value = f"https://{platform}.com/video123"
            manager.uploaders[platform] = mock_up

        results = manager.upload_to_all(
            video_path=self.video_path,
            title="Integration Test Video",
            description="Testing upload pipeline",
            tags=["test"],
            hashtags=["integration"],
        )

        assert len(results) == 3
        assert all(url is not None for url in results.values())

    def test_partial_platform_failure(self, mock_config):
        from uploaders.upload_manager import UploadManager

        manager = UploadManager()

        for platform in manager.uploaders:
            mock_up = MagicMock()
            if platform == "tiktok":
                mock_up.safe_upload.return_value = None  # TikTok fails
            else:
                mock_up.safe_upload.return_value = f"https://{platform}.com/v"
            manager.uploaders[platform] = mock_up

        results = manager.upload_to_all(
            video_path=self.video_path,
            title="Partial Test",
        )

        assert results["tiktok"] is None
        # Other platforms should still succeed
        success_count = sum(1 for v in results.values() if v is not None)
        assert success_count >= 1

    def test_metadata_is_correct(self, mock_config):
        from uploaders.upload_manager import UploadManager

        manager = UploadManager()

        captured_metadata = {}
        for platform in manager.uploaders:
            mock_up = MagicMock()

            def capture(m, name=platform):
                captured_metadata[name] = m
                return f"https://{name}.com/v"

            mock_up.safe_upload.side_effect = capture
            manager.uploaders[platform] = mock_up

        manager.upload_to_all(
            video_path=self.video_path,
            title="Metadata Test",
            description="Test desc",
            tags=["tag1"],
            hashtags=["hash1"],
            privacy="private",
        )

        for name, m in captured_metadata.items():
            assert isinstance(m, VideoMetadata)
            assert m.title == "Metadata Test"
            assert m.description == "Test desc"
            assert m.privacy == "private"
            assert "hash1" in m.hashtags


# ===================================================================
# YouTube upload integration
# ===================================================================


class TestYouTubeUploadIntegration:
    """Test YouTube upload flow with mocked requests."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config, sample_video_file):
        mock_config["uploaders"]["youtube"]["enabled"] = True
        self.video_path = sample_video_file

    def test_full_youtube_upload_flow(self):
        from uploaders.youtube_uploader import YouTubeUploader

        uploader = YouTubeUploader()

        with patch("uploaders.youtube_uploader.requests.post") as mock_post, \
             patch("uploaders.youtube_uploader.requests.put") as mock_put:

            # Auth response
            auth_resp = MagicMock()
            auth_resp.json.return_value = {"access_token": "yt_token"}
            auth_resp.raise_for_status = MagicMock()

            # Init upload response
            init_resp = MagicMock()
            init_resp.headers = {"Location": "https://upload.youtube.com/session123"}
            init_resp.raise_for_status = MagicMock()

            mock_post.side_effect = [auth_resp, init_resp]

            # Upload response
            upload_resp = MagicMock()
            upload_resp.json.return_value = {"id": "yt_video_id_123"}
            upload_resp.raise_for_status = MagicMock()
            mock_put.return_value = upload_resp

            uploader.authenticate()
            m = VideoMetadata(file_path=self.video_path, title="YT Test")
            url = uploader.upload(m)

            assert url == "https://www.youtube.com/watch?v=yt_video_id_123"


# ===================================================================
# TikTok upload integration
# ===================================================================


class TestTikTokUploadIntegration:
    """Test TikTok upload flow with mocked requests."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config, sample_video_file):
        mock_config["uploaders"]["tiktok"]["enabled"] = True
        self.video_path = sample_video_file

    def test_full_tiktok_upload_flow(self):
        from uploaders.tiktok_uploader import TikTokUploader

        uploader = TikTokUploader()

        with patch("uploaders.tiktok_uploader.requests.post") as mock_post, \
             patch("uploaders.tiktok_uploader.requests.put") as mock_put, \
             patch("uploaders.tiktok_uploader.time.sleep"):

            # Auth response
            auth_resp = MagicMock()
            auth_resp.json.return_value = {"data": {"access_token": "tt_token"}}
            auth_resp.raise_for_status = MagicMock()

            # Init upload response
            init_resp = MagicMock()
            init_resp.json.return_value = {
                "data": {"publish_id": "pub_123", "upload_url": "https://upload.tiktok.com/xyz"}
            }
            init_resp.raise_for_status = MagicMock()

            # Status check response
            status_resp = MagicMock()
            status_resp.json.return_value = {"data": {"status": "PUBLISH_COMPLETE"}}

            mock_post.side_effect = [auth_resp, init_resp, status_resp]
            mock_put.return_value = MagicMock(raise_for_status=MagicMock())

            uploader.authenticate()
            m = VideoMetadata(file_path=self.video_path, title="TT Test")
            url = uploader.upload(m)

            assert url is not None
            assert url.startswith("https://www.tiktok.com/")


# ===================================================================
# Facebook upload integration
# ===================================================================


class TestFacebookUploadIntegration:
    """Test Facebook upload flow with mocked requests."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config, sample_video_file):
        mock_config["uploaders"]["facebook"]["enabled"] = True
        self.video_path = sample_video_file

    def test_full_facebook_upload_flow(self):
        from uploaders.facebook_uploader import FacebookUploader

        uploader = FacebookUploader()

        with patch("uploaders.facebook_uploader.requests.get") as mock_get, \
             patch("uploaders.facebook_uploader.requests.post") as mock_post:

            # Auth verify response
            auth_resp = MagicMock()
            auth_resp.json.return_value = {"id": "page_123", "name": "Test Page"}
            auth_resp.raise_for_status = MagicMock()
            mock_get.return_value = auth_resp

            # Init upload
            init_resp = MagicMock()
            init_resp.json.return_value = {
                "upload_session_id": "sess_123",
                "video_id": "vid_456",
            }
            init_resp.raise_for_status = MagicMock()

            # Transfer chunk
            transfer_resp = MagicMock()
            transfer_resp.json.return_value = {
                "start_offset": str(1024),  # File is 1KB, so this ends transfer
                "end_offset": str(1024),
            }
            transfer_resp.raise_for_status = MagicMock()

            # Finish
            finish_resp = MagicMock()
            finish_resp.json.return_value = {"success": True}
            finish_resp.raise_for_status = MagicMock()

            mock_post.side_effect = [init_resp, transfer_resp, finish_resp]

            uploader.authenticate()
            m = VideoMetadata(file_path=self.video_path, title="FB Test")
            url = uploader.upload(m)

            assert url is not None
            assert url.startswith("https://www.facebook.com/")
