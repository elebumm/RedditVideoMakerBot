"""
Unit tests for utils/videos.py — Video deduplication and metadata storage.
"""

import json
import os
from unittest.mock import mock_open, patch

import pytest


class TestCheckDone:
    def test_returns_id_when_not_done(self, mock_config, tmp_path):
        from utils.videos import check_done

        videos_data = json.dumps([])
        with patch("builtins.open", mock_open(read_data=videos_data)):
            result = check_done("new_thread_id")
        assert result == "new_thread_id"

    def test_returns_none_when_already_done(self, mock_config, tmp_path):
        from utils.videos import check_done

        videos_data = json.dumps([{"id": "existing_id", "subreddit": "test"}])
        with patch("builtins.open", mock_open(read_data=videos_data)):
            result = check_done("existing_id")
        assert result is None

    def test_returns_obj_when_post_id_specified(self, mock_config):
        from utils.videos import check_done

        mock_config["threads"]["thread"]["post_id"] = "specific_post"
        videos_data = json.dumps([{"id": "existing_id", "subreddit": "test"}])
        with patch("builtins.open", mock_open(read_data=videos_data)):
            result = check_done("existing_id")
        assert result == "existing_id"


class TestSaveData:
    def test_saves_video_metadata(self, mock_config, tmp_path):
        from utils.videos import save_data

        videos_file = str(tmp_path / "videos.json")
        with open(videos_file, "w", encoding="utf-8") as f:
            json.dump([], f)

        m = mock_open(read_data=json.dumps([]))
        m.return_value.seek = lambda pos: None

        with patch("builtins.open", m):
            save_data("test_channel", "output.mp4", "Test Title", "thread_123", "minecraft")

        # Verify write was called with the new data
        write_calls = m().write.call_args_list
        assert len(write_calls) > 0
        written_data = "".join(call.args[0] for call in write_calls)
        parsed = json.loads(written_data)
        assert len(parsed) == 1
        assert parsed[0]["id"] == "thread_123"

    def test_skips_duplicate_id(self, mock_config):
        from utils.videos import save_data

        existing = [{"id": "thread_123", "subreddit": "test", "time": "1000",
                     "background_credit": "", "reddit_title": "", "filename": ""}]
        m = mock_open(read_data=json.dumps(existing))
        with patch("builtins.open", m):
            save_data("test_channel", "output2.mp4", "Another Title", "thread_123", "gta")

        # Verify no new data was written (duplicate ID skipped)
        assert not m().write.called
