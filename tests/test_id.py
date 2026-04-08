"""
Unit tests for utils/id.py — Thread/post ID extraction.
"""

import pytest

from utils.id import extract_id


class TestExtractId:
    def test_extracts_thread_id(self):
        obj = {"thread_id": "ABC123"}
        assert extract_id(obj) == "ABC123"

    def test_extracts_custom_field(self):
        obj = {"custom_field": "XYZ789"}
        assert extract_id(obj, field="custom_field") == "XYZ789"

    def test_strips_special_characters(self):
        obj = {"thread_id": "abc!@#$%^&*()123"}
        result = extract_id(obj)
        assert "!" not in result
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
        # Alphanumeric and hyphens/underscores/whitespace should remain
        assert "abc" in result
        assert "123" in result

    def test_raises_for_missing_field(self):
        obj = {"other_field": "value"}
        with pytest.raises(ValueError, match="Field 'thread_id' not found"):
            extract_id(obj)

    def test_handles_empty_string_id(self):
        obj = {"thread_id": ""}
        result = extract_id(obj)
        assert result == ""

    def test_preserves_hyphens_and_underscores(self):
        obj = {"thread_id": "test-thread_123"}
        result = extract_id(obj)
        assert result == "test-thread_123"

    def test_preserves_whitespace(self):
        obj = {"thread_id": "test thread 123"}
        result = extract_id(obj)
        assert "test thread 123" == result
