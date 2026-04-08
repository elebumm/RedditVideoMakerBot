"""
Unit tests for utils/check_token.py — Preflight access token validation.

All external API calls are mocked.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from utils.check_token import TokenCheckError, _call_me_endpoint, _try_refresh


# ===================================================================
# _call_me_endpoint
# ===================================================================


class TestCallMeEndpoint:
    def test_successful_call(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "123456",
            "username": "testuser",
            "name": "Test User",
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("utils.check_token.requests.get", return_value=mock_resp):
            result = _call_me_endpoint("valid_token")
            assert result["username"] == "testuser"

    def test_401_raises_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        with patch("utils.check_token.requests.get", return_value=mock_resp):
            with pytest.raises(TokenCheckError, match="401"):
                _call_me_endpoint("bad_token")

    def test_403_raises_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        with patch("utils.check_token.requests.get", return_value=mock_resp):
            with pytest.raises(TokenCheckError, match="403"):
                _call_me_endpoint("bad_token")

    def test_200_with_error_body(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "error": {"message": "Token expired", "code": 190}
        }
        mock_resp.raise_for_status = MagicMock()
        with patch("utils.check_token.requests.get", return_value=mock_resp):
            with pytest.raises(TokenCheckError, match="Token expired"):
                _call_me_endpoint("expired_token")


# ===================================================================
# _try_refresh
# ===================================================================


class TestTryRefresh:
    def test_successful_refresh(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access_token": "new_token_456"}
        mock_resp.raise_for_status = MagicMock()
        with patch("utils.check_token.requests.get", return_value=mock_resp):
            result = _try_refresh("old_token")
            assert result == "new_token_456"

    def test_returns_none_on_error_body(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"error": {"message": "Cannot refresh"}}
        mock_resp.raise_for_status = MagicMock()
        with patch("utils.check_token.requests.get", return_value=mock_resp):
            result = _try_refresh("old_token")
            assert result is None

    def test_returns_none_on_request_exception(self):
        with patch(
            "utils.check_token.requests.get",
            side_effect=requests.RequestException("Network error"),
        ):
            result = _try_refresh("old_token")
            assert result is None

    def test_returns_none_when_no_token_in_response(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"token_type": "bearer"}  # no access_token
        mock_resp.raise_for_status = MagicMock()
        with patch("utils.check_token.requests.get", return_value=mock_resp):
            result = _try_refresh("old_token")
            assert result is None


# ===================================================================
# preflight_check
# ===================================================================


class TestPreflightCheck:
    def test_success(self, mock_config):
        from utils.check_token import preflight_check

        with patch("utils.check_token._call_me_endpoint") as mock_me:
            mock_me.return_value = {"id": "123456789", "username": "testuser"}
            # Should not raise
            preflight_check()

    def test_exits_when_token_empty(self, mock_config):
        from utils.check_token import preflight_check

        mock_config["threads"]["creds"]["access_token"] = ""
        with pytest.raises(SystemExit):
            preflight_check()

    def test_exits_when_user_id_empty(self, mock_config):
        from utils.check_token import preflight_check

        mock_config["threads"]["creds"]["user_id"] = ""
        with pytest.raises(SystemExit):
            preflight_check()

    def test_refresh_on_invalid_token(self, mock_config):
        from utils.check_token import preflight_check

        with patch("utils.check_token._call_me_endpoint") as mock_me, \
             patch("utils.check_token._try_refresh") as mock_refresh:
            # First call fails, refresh works, second call succeeds
            mock_me.side_effect = [
                TokenCheckError("Token expired"),
                {"id": "123456789", "username": "testuser"},
            ]
            mock_refresh.return_value = "new_token"
            preflight_check()
            assert mock_config["threads"]["creds"]["access_token"] == "new_token"

    def test_exits_when_refresh_fails(self, mock_config):
        from utils.check_token import preflight_check

        with patch("utils.check_token._call_me_endpoint") as mock_me, \
             patch("utils.check_token._try_refresh") as mock_refresh:
            mock_me.side_effect = TokenCheckError("Token expired")
            mock_refresh.return_value = None
            with pytest.raises(SystemExit):
                preflight_check()

    def test_exits_on_network_error(self, mock_config):
        from utils.check_token import preflight_check

        with patch("utils.check_token._call_me_endpoint") as mock_me:
            mock_me.side_effect = requests.RequestException("Network error")
            with pytest.raises(SystemExit):
                preflight_check()
