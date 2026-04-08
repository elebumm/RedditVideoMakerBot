"""
Unit tests for Threads API Client (threads/threads_client.py).

All HTTP calls are mocked — no real API requests are made.
"""

import copy
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
import requests

from tests.conftest import MOCK_CONFIG


# ===================================================================
# Helper: Build a mock HTTP response
# ===================================================================


def _mock_response(status_code=200, json_data=None, headers=None):
    """Create a mock requests.Response."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.headers = headers or {}
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}", response=resp
        )
    return resp


# ===================================================================
# ThreadsAPIError
# ===================================================================


class TestThreadsAPIError:
    def test_basic_creation(self):
        from threads.threads_client import ThreadsAPIError

        err = ThreadsAPIError("test error", error_type="OAuthException", error_code=401)
        assert str(err) == "test error"
        assert err.error_type == "OAuthException"
        assert err.error_code == 401

    def test_defaults(self):
        from threads.threads_client import ThreadsAPIError

        err = ThreadsAPIError("simple error")
        assert err.error_type == ""
        assert err.error_code == 0


# ===================================================================
# ThreadsClient._handle_api_response
# ===================================================================


class TestHandleApiResponse:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_success_response(self):
        resp = _mock_response(200, {"data": [{"id": "1"}]})
        result = self.client._handle_api_response(resp)
        assert result == {"data": [{"id": "1"}]}

    def test_401_raises_api_error(self):
        from threads.threads_client import ThreadsAPIError

        resp = _mock_response(401)
        with pytest.raises(ThreadsAPIError, match="401"):
            self.client._handle_api_response(resp)

    def test_403_raises_api_error(self):
        from threads.threads_client import ThreadsAPIError

        resp = _mock_response(403)
        with pytest.raises(ThreadsAPIError, match="403"):
            self.client._handle_api_response(resp)

    def test_200_with_error_body(self):
        from threads.threads_client import ThreadsAPIError

        resp = _mock_response(
            200,
            {"error": {"message": "Invalid token", "type": "OAuthException", "code": 190}},
        )
        with pytest.raises(ThreadsAPIError, match="Invalid token"):
            self.client._handle_api_response(resp)


# ===================================================================
# ThreadsClient._get and _post with retry logic
# ===================================================================


class TestGetWithRetry:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_successful_get(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _mock_response(200, {"id": "123"})
            result = self.client._get("me", params={"fields": "id"})
            assert result == {"id": "123"}
            mock_get.assert_called_once()

    def test_retries_on_connection_error(self):
        with patch.object(self.client.session, "get") as mock_get, \
             patch("threads.threads_client._time.sleep"):
            # Fail twice, succeed on third
            mock_get.side_effect = [
                requests.ConnectionError("Connection failed"),
                requests.ConnectionError("Connection failed"),
                _mock_response(200, {"id": "123"}),
            ]
            result = self.client._get("me")
            assert result == {"id": "123"}
            assert mock_get.call_count == 3

    def test_raises_after_max_retries(self):
        with patch.object(self.client.session, "get") as mock_get, \
             patch("threads.threads_client._time.sleep"):
            mock_get.side_effect = requests.ConnectionError("Connection failed")
            with pytest.raises(requests.ConnectionError):
                self.client._get("me")
            assert mock_get.call_count == 3  # _MAX_RETRIES

    def test_does_not_retry_api_error(self):
        from threads.threads_client import ThreadsAPIError

        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _mock_response(
                200, {"error": {"message": "Bad request", "type": "APIError", "code": 100}}
            )
            with pytest.raises(ThreadsAPIError):
                self.client._get("me")
            assert mock_get.call_count == 1  # No retries for API errors


class TestPostWithRetry:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_successful_post(self):
        with patch.object(self.client.session, "post") as mock_post:
            mock_post.return_value = _mock_response(200, {"id": "container_123"})
            result = self.client._post("user/threads", data={"text": "Hello"})
            assert result == {"id": "container_123"}


# ===================================================================
# ThreadsClient._get_paginated
# ===================================================================


class TestGetPaginated:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_single_page(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {
                "data": [{"id": "1"}, {"id": "2"}],
                "paging": {},
            }
            result = self.client._get_paginated("user/threads", max_items=10)
            assert len(result) == 2

    def test_multi_page(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.side_effect = [
                {
                    "data": [{"id": "1"}, {"id": "2"}],
                    "paging": {"cursors": {"after": "cursor1"}, "next": "url"},
                },
                {
                    "data": [{"id": "3"}],
                    "paging": {},
                },
            ]
            result = self.client._get_paginated("user/threads", max_items=10)
            assert len(result) == 3

    def test_respects_max_items(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {
                "data": [{"id": str(i)} for i in range(50)],
                "paging": {"cursors": {"after": "c"}, "next": "url"},
            }
            result = self.client._get_paginated("user/threads", max_items=5)
            assert len(result) == 5

    def test_empty_data(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {"data": [], "paging": {}}
            result = self.client._get_paginated("user/threads", max_items=10)
            assert result == []


# ===================================================================
# Token Management
# ===================================================================


class TestValidateToken:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_validate_success(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {
                "id": "123456789",
                "username": "testuser",
                "name": "Test User",
            }
            result = self.client.validate_token()
            assert result["username"] == "testuser"

    def test_validate_fails_with_bad_token(self):
        from threads.threads_client import ThreadsAPIError

        with patch.object(self.client, "_get") as mock_get:
            mock_get.side_effect = ThreadsAPIError("Token expired")
            with pytest.raises(ThreadsAPIError, match="token"):
                self.client.validate_token()


class TestRefreshToken:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_refresh_success(self):
        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _mock_response(
                200, {"access_token": "new_token_123", "token_type": "bearer", "expires_in": 5184000}
            )
            new_token = self.client.refresh_token()
            assert new_token == "new_token_123"
            assert self.client.access_token == "new_token_123"

    def test_refresh_failure_error_body(self):
        from threads.threads_client import ThreadsAPIError

        with patch.object(self.client.session, "get") as mock_get:
            mock_get.return_value = _mock_response(
                200, {"error": {"message": "Token cannot be refreshed"}}
            )
            with pytest.raises(ThreadsAPIError, match="refresh"):
                self.client.refresh_token()


# ===================================================================
# Profiles API
# ===================================================================


class TestGetUserProfile:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_get_own_profile(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {"id": "123", "username": "testuser"}
            result = self.client.get_user_profile()
            mock_get.assert_called_once()
            assert result["username"] == "testuser"

    def test_get_specific_user_profile(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {"id": "456", "username": "other_user"}
            result = self.client.get_user_profile(user_id="456")
            assert result["id"] == "456"


# ===================================================================
# Media API
# ===================================================================


class TestGetUserThreads:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_get_user_threads(self):
        with patch.object(self.client, "_get_paginated") as mock_paginated:
            mock_paginated.return_value = [{"id": "1", "text": "Hello"}]
            result = self.client.get_user_threads(limit=10)
            assert len(result) == 1
            assert result[0]["text"] == "Hello"


class TestGetThreadById:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_get_thread_details(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {"id": "thread_1", "text": "Thread content", "has_replies": True}
            result = self.client.get_thread_by_id("thread_1")
            assert result["text"] == "Thread content"


# ===================================================================
# Reply Management
# ===================================================================


class TestGetThreadReplies:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_get_replies(self):
        with patch.object(self.client, "_get_paginated") as mock_paginated:
            mock_paginated.return_value = [
                {"id": "r1", "text": "Reply 1"},
                {"id": "r2", "text": "Reply 2"},
            ]
            result = self.client.get_thread_replies("thread_1")
            assert len(result) == 2


class TestGetConversation:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_get_full_conversation(self):
        with patch.object(self.client, "_get_paginated") as mock_paginated:
            mock_paginated.return_value = [
                {"id": "r1", "text": "Reply 1"},
                {"id": "r2", "text": "Nested reply"},
            ]
            result = self.client.get_conversation("thread_1")
            assert len(result) == 2


class TestManageReply:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_hide_reply(self):
        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = {"success": True}
            result = self.client.manage_reply("reply_1", hide=True)
            assert result["success"] is True
            mock_post.assert_called_once_with(
                "reply_1/manage_reply", data={"hide": "true"}
            )

    def test_unhide_reply(self):
        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = {"success": True}
            self.client.manage_reply("reply_1", hide=False)
            mock_post.assert_called_once_with(
                "reply_1/manage_reply", data={"hide": "false"}
            )


# ===================================================================
# Publishing API
# ===================================================================


class TestCreateContainer:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_create_text_container(self):
        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = {"id": "container_123"}
            cid = self.client.create_container(text="Hello world")
            assert cid == "container_123"

    def test_create_image_container(self):
        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = {"id": "container_456"}
            cid = self.client.create_container(
                media_type="IMAGE",
                text="Photo caption",
                image_url="https://example.com/image.jpg",
            )
            assert cid == "container_456"

    def test_raises_when_no_id_returned(self):
        from threads.threads_client import ThreadsAPIError

        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = {}
            with pytest.raises(ThreadsAPIError, match="container ID"):
                self.client.create_container(text="Test")


class TestPublishThread:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_publish_success(self):
        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = {"id": "published_thread_1"}
            media_id = self.client.publish_thread("container_123")
            assert media_id == "published_thread_1"

    def test_publish_no_id(self):
        from threads.threads_client import ThreadsAPIError

        with patch.object(self.client, "_post") as mock_post:
            mock_post.return_value = {}
            with pytest.raises(ThreadsAPIError, match="media ID"):
                self.client.publish_thread("container_123")


# ===================================================================
# Insights API
# ===================================================================


class TestGetThreadInsights:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_get_insights(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {
                "data": [
                    {"name": "views", "values": [{"value": 1000}]},
                    {"name": "likes", "values": [{"value": 50}]},
                ]
            }
            result = self.client.get_thread_insights("thread_1")
            assert len(result) == 2


class TestGetThreadEngagement:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_engagement_dict(self):
        with patch.object(self.client, "get_thread_insights") as mock_insights:
            mock_insights.return_value = [
                {"name": "views", "values": [{"value": 1000}]},
                {"name": "likes", "values": [{"value": 50}]},
                {"name": "replies", "values": [{"value": 10}]},
            ]
            engagement = self.client.get_thread_engagement("thread_1")
            assert engagement["views"] == 1000
            assert engagement["likes"] == 50
            assert engagement["replies"] == 10


# ===================================================================
# Rate Limiting
# ===================================================================


class TestCanPublish:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_can_publish_when_quota_available(self):
        with patch.object(self.client, "get_publishing_limit") as mock_limit:
            mock_limit.return_value = {
                "quota_usage": 10,
                "config": {"quota_total": 250},
            }
            assert self.client.can_publish() is True

    def test_cannot_publish_when_quota_exhausted(self):
        with patch.object(self.client, "get_publishing_limit") as mock_limit:
            mock_limit.return_value = {
                "quota_usage": 250,
                "config": {"quota_total": 250},
            }
            assert self.client.can_publish() is False

    def test_optimistic_on_error(self):
        from threads.threads_client import ThreadsAPIError

        with patch.object(self.client, "get_publishing_limit") as mock_limit:
            mock_limit.side_effect = ThreadsAPIError("Rate limit error")
            assert self.client.can_publish() is True


# ===================================================================
# Keyword Search API
# ===================================================================


class TestKeywordSearch:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_basic_search(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {
                "data": [
                    {"id": "1", "text": "Search result 1"},
                    {"id": "2", "text": "Search result 2"},
                ]
            }
            results = self.client.keyword_search("test query")
            assert len(results) == 2

    def test_empty_query_raises(self):
        with pytest.raises(ValueError, match="bắt buộc"):
            self.client.keyword_search("")

    def test_whitespace_query_raises(self):
        with pytest.raises(ValueError, match="bắt buộc"):
            self.client.keyword_search("   ")

    def test_invalid_search_type_raises(self):
        with pytest.raises(ValueError, match="search_type"):
            self.client.keyword_search("test", search_type="INVALID")

    def test_invalid_search_mode_raises(self):
        with pytest.raises(ValueError, match="search_mode"):
            self.client.keyword_search("test", search_mode="INVALID")

    def test_invalid_media_type_raises(self):
        with pytest.raises(ValueError, match="media_type"):
            self.client.keyword_search("test", media_type="INVALID")

    def test_invalid_limit_raises(self):
        with pytest.raises(ValueError, match="limit"):
            self.client.keyword_search("test", limit=0)
        with pytest.raises(ValueError, match="limit"):
            self.client.keyword_search("test", limit=101)

    def test_strips_at_from_username(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {"data": []}
            self.client.keyword_search("test", author_username="@testuser")
            call_params = mock_get.call_args[1]["params"]
            assert call_params["author_username"] == "testuser"

    def test_search_with_all_params(self):
        with patch.object(self.client, "_get") as mock_get:
            mock_get.return_value = {"data": [{"id": "1"}]}
            results = self.client.keyword_search(
                q="trending",
                search_type="RECENT",
                search_mode="TAG",
                media_type="TEXT",
                since="1700000000",
                until="1700100000",
                limit=50,
                author_username="user",
            )
            assert len(results) == 1


# ===================================================================
# Client-side keyword filter
# ===================================================================


class TestSearchThreadsByKeyword:
    @pytest.fixture(autouse=True)
    def _setup(self, mock_config):
        from threads.threads_client import ThreadsClient

        self.client = ThreadsClient()

    def test_filters_by_keyword(self):
        threads = [
            {"id": "1", "text": "Python is great for AI"},
            {"id": "2", "text": "JavaScript frameworks"},
            {"id": "3", "text": "Learning Python basics"},
        ]
        result = self.client.search_threads_by_keyword(threads, ["python"])
        assert len(result) == 2

    def test_case_insensitive_filter(self):
        threads = [{"id": "1", "text": "PYTHON Programming"}]
        result = self.client.search_threads_by_keyword(threads, ["python"])
        assert len(result) == 1

    def test_no_match(self):
        threads = [{"id": "1", "text": "JavaScript only"}]
        result = self.client.search_threads_by_keyword(threads, ["python"])
        assert len(result) == 0

    def test_multiple_keywords(self):
        threads = [
            {"id": "1", "text": "Python programming"},
            {"id": "2", "text": "Java development"},
            {"id": "3", "text": "Rust is fast"},
        ]
        result = self.client.search_threads_by_keyword(threads, ["python", "rust"])
        assert len(result) == 2


# ===================================================================
# _contains_blocked_words
# ===================================================================


class TestContainsBlockedWords:
    def test_no_blocked_words(self, mock_config):
        from threads.threads_client import _contains_blocked_words

        mock_config["threads"]["thread"]["blocked_words"] = ""
        assert _contains_blocked_words("any text here") is False

    def test_detects_blocked_word(self, mock_config):
        from threads.threads_client import _contains_blocked_words

        mock_config["threads"]["thread"]["blocked_words"] = "spam, scam, fake"
        assert _contains_blocked_words("This is spam content") is True

    def test_case_insensitive(self, mock_config):
        from threads.threads_client import _contains_blocked_words

        mock_config["threads"]["thread"]["blocked_words"] = "spam"
        assert _contains_blocked_words("SPAM HERE") is True

    def test_no_match(self, mock_config):
        from threads.threads_client import _contains_blocked_words

        mock_config["threads"]["thread"]["blocked_words"] = "spam, scam"
        assert _contains_blocked_words("Clean text") is False
