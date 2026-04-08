"""
Integration tests for Threads API external calls — mocked HTTP layer.

Tests the full request flow through ThreadsClient including URL construction,
parameter passing, pagination, and error handling.
"""

import json
from unittest.mock import MagicMock, call, patch

import pytest
import requests

from tests.conftest import MOCK_CONFIG


def _fake_response(status_code=200, json_data=None, headers=None):
    """Build a realistic requests.Response mock."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.headers = headers or {}
    if status_code < 400:
        resp.raise_for_status = MagicMock()
    else:
        resp.raise_for_status = MagicMock(
            side_effect=requests.HTTPError(f"{status_code}", response=resp)
        )
    return resp


# ===================================================================
# Full request flow — GET endpoints
# ===================================================================


class TestThreadsAPIIntegrationGet:
    """Integration tests verifying URL construction and parameter passing."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_get_user_profile_calls_correct_endpoint(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(
                200, {"id": "123", "username": "user"}
            )
            self.client.get_user_profile()
            call_url = mock_get.call_args[0][0]
            assert "/me" in call_url
            params = mock_get.call_args[1]["params"]
            assert "fields" in params
            assert "id" in params["fields"]

    def test_get_user_threads_calls_correct_endpoint(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(
                200, {"data": [{"id": "1"}], "paging": {}}
            )
            self.client.get_user_threads(limit=5)
            call_url = mock_get.call_args[0][0]
            assert "/threads" in call_url

    def test_get_thread_replies_includes_reverse_param(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(
                200, {"data": [], "paging": {}}
            )
            self.client.get_thread_replies("t1", reverse=True)
            params = mock_get.call_args[1]["params"]
            assert params.get("reverse") == "true"

    def test_get_conversation_calls_conversation_endpoint(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(
                200, {"data": [], "paging": {}}
            )
            self.client.get_conversation("t1")
            call_url = mock_get.call_args[0][0]
            assert "/conversation" in call_url

    def test_get_thread_insights_calls_insights_endpoint(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(
                200, {"data": [{"name": "views", "values": [{"value": 100}]}]}
            )
            self.client.get_thread_insights("t1")
            call_url = mock_get.call_args[0][0]
            assert "/insights" in call_url

    def test_get_publishing_limit_calls_correct_endpoint(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(
                200, {"data": [{"quota_usage": 10, "config": {"quota_total": 250}}]}
            )
            self.client.get_publishing_limit()
            call_url = mock_get.call_args[0][0]
            assert "/threads_publishing_limit" in call_url

    def test_keyword_search_calls_correct_endpoint(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(200, {"data": []})
            self.client.keyword_search("test query")
            call_url = mock_get.call_args[0][0]
            assert "/threads_keyword_search" in call_url
            params = mock_get.call_args[1]["params"]
            assert params["q"] == "test query"


# ===================================================================
# Full request flow — POST endpoints
# ===================================================================


class TestThreadsAPIIntegrationPost:
    """Integration tests verifying POST request construction."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_create_container_sends_post(self):
        with patch.object(self.client.session, "post") as mock_post:
            mock_post.return_value = _fake_response(200, {"id": "c1"})
            self.client.create_container(text="Hello")
            call_url = mock_post.call_args[0][0]
            assert "/threads" in call_url
            data = mock_post.call_args[1]["data"]
            assert data["text"] == "Hello"
            assert data["media_type"] == "TEXT"

    def test_publish_thread_sends_creation_id(self):
        with patch.object(self.client.session, "post") as mock_post:
            mock_post.return_value = _fake_response(200, {"id": "pub_1"})
            self.client.publish_thread("c1")
            data = mock_post.call_args[1]["data"]
            assert data["creation_id"] == "c1"

    def test_manage_reply_sends_hide_true(self):
        with patch.object(self.client.session, "post") as mock_post:
            mock_post.return_value = _fake_response(200, {"success": True})
            self.client.manage_reply("r1", hide=True)
            call_url = mock_post.call_args[0][0]
            assert "/manage_reply" in call_url


# ===================================================================
# create_and_publish flow
# ===================================================================


class TestCreateAndPublishFlow:
    """Integration test for the full create → poll → publish flow."""

    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_text_post_flow(self):
        with patch.object(self.client, "create_container") as mock_create, \
             patch.object(self.client, "publish_thread") as mock_publish:
            mock_create.return_value = "c1"
            mock_publish.return_value = "pub_1"
            result = self.client.create_and_publish(text="Hello world")
            assert result == "pub_1"
            mock_create.assert_called_once()
            mock_publish.assert_called_once_with("c1")

    def test_image_post_polls_status(self):
        with patch.object(self.client, "create_container") as mock_create, \
             patch.object(self.client, "get_container_status") as mock_status, \
             patch.object(self.client, "publish_thread") as mock_publish, \
             patch("threads.threads_client._time.sleep"):
            mock_create.return_value = "c1"
            mock_status.side_effect = [
                {"status": "IN_PROGRESS"},
                {"status": "FINISHED"},
            ]
            mock_publish.return_value = "pub_2"
            result = self.client.create_and_publish(
                text="Photo", image_url="https://example.com/img.jpg"
            )
            assert result == "pub_2"
            assert mock_status.call_count == 2

    def test_container_error_raises(self):
        from threads.threads_client import ThreadsAPIError

        with patch.object(self.client, "create_container") as mock_create, \
             patch.object(self.client, "get_container_status") as mock_status, \
             patch("threads.threads_client._time.sleep"):
            mock_create.return_value = "c1"
            mock_status.return_value = {
                "status": "ERROR",
                "error_message": "Invalid image format",
            }
            with pytest.raises(ThreadsAPIError, match="lỗi"):
                self.client.create_and_publish(
                    image_url="https://example.com/bad.jpg"
                )


# ===================================================================
# Token refresh integration
# ===================================================================


class TestTokenRefreshIntegration:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_refresh_updates_config(self, mock_config):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _fake_response(
                200, {"access_token": "refreshed_token", "expires_in": 5184000}
            )
            new_token = self.client.refresh_token()
            assert new_token == "refreshed_token"
            assert mock_config["threads"]["creds"]["access_token"] == "refreshed_token"


# ===================================================================
# Pagination integration
# ===================================================================


class TestPaginationIntegration:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_paginated_uses_cursor(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.side_effect = [
                _fake_response(200, {
                    "data": [{"id": str(i)} for i in range(3)],
                    "paging": {"cursors": {"after": "cursor_abc"}, "next": "next_url"},
                }),
                _fake_response(200, {
                    "data": [{"id": str(i)} for i in range(3, 5)],
                    "paging": {},
                }),
            ]
            result = self.client._get_paginated("user/threads", max_items=10)
            assert len(result) == 5
            # Second call should include the cursor
            second_call_params = mock_get.call_args_list[1][1]["params"]
            assert second_call_params.get("after") == "cursor_abc"


# ===================================================================
# Error handling integration
# ===================================================================


class TestErrorHandlingIntegration:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_timeout_retries(self):
        with patch.object(self.client.session, "get") as mock_get, \
             patch("threads.threads_client._time.sleep"):
            mock_get.side_effect = [
                requests.Timeout("Request timed out"),
                _fake_response(200, {"id": "ok"}),
            ]
            result = self.client._get("me")
            assert result == {"id": "ok"}
            assert mock_get.call_count == 2
