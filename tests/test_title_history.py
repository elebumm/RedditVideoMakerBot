"""
Unit tests for utils/title_history.py — Title deduplication system.
"""

import json
import os
from unittest.mock import patch

import pytest

from utils.title_history import (
    TITLE_HISTORY_PATH,
    _ensure_file_exists,
    get_title_count,
    is_title_used,
    load_title_history,
    save_title,
)


@pytest.fixture
def patched_history_path(tmp_path):
    """Redirect title history to a temporary file."""
    history_file = str(tmp_path / "title_history.json")
    with patch("utils.title_history.TITLE_HISTORY_PATH", history_file):
        yield history_file


# ===================================================================
# _ensure_file_exists
# ===================================================================


class TestEnsureFileExists:
    def test_creates_file_when_missing(self, patched_history_path):
        assert not os.path.exists(patched_history_path)
        _ensure_file_exists()
        assert os.path.exists(patched_history_path)
        with open(patched_history_path, "r", encoding="utf-8") as f:
            assert json.load(f) == []

    def test_no_op_when_file_exists(self, patched_history_path):
        # Pre-create with data
        os.makedirs(os.path.dirname(patched_history_path), exist_ok=True)
        with open(patched_history_path, "w", encoding="utf-8") as f:
            json.dump([{"title": "existing"}], f)
        _ensure_file_exists()
        with open(patched_history_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["title"] == "existing"


# ===================================================================
# load_title_history
# ===================================================================


class TestLoadTitleHistory:
    def test_returns_empty_list_on_fresh_state(self, patched_history_path):
        result = load_title_history()
        assert result == []

    def test_returns_saved_data(self, patched_history_path):
        os.makedirs(os.path.dirname(patched_history_path), exist_ok=True)
        entries = [{"title": "Test Title", "thread_id": "123", "source": "threads", "created_at": 1000}]
        with open(patched_history_path, "w", encoding="utf-8") as f:
            json.dump(entries, f)
        result = load_title_history()
        assert len(result) == 1
        assert result[0]["title"] == "Test Title"

    def test_handles_corrupted_json(self, patched_history_path):
        os.makedirs(os.path.dirname(patched_history_path), exist_ok=True)
        with open(patched_history_path, "w") as f:
            f.write("not valid json!!!")
        result = load_title_history()
        assert result == []


# ===================================================================
# is_title_used
# ===================================================================


class TestIsTitleUsed:
    def test_returns_false_for_empty_title(self, patched_history_path):
        assert is_title_used("") is False
        assert is_title_used("   ") is False

    def test_returns_false_when_history_empty(self, patched_history_path):
        assert is_title_used("New Title") is False

    def test_returns_true_for_exact_match(self, patched_history_path):
        os.makedirs(os.path.dirname(patched_history_path), exist_ok=True)
        with open(patched_history_path, "w", encoding="utf-8") as f:
            json.dump([{"title": "Existing Title", "thread_id": "", "source": "threads", "created_at": 1000}], f)
        assert is_title_used("Existing Title") is True

    def test_case_insensitive_match(self, patched_history_path):
        os.makedirs(os.path.dirname(patched_history_path), exist_ok=True)
        with open(patched_history_path, "w", encoding="utf-8") as f:
            json.dump([{"title": "Existing Title", "thread_id": "", "source": "threads", "created_at": 1000}], f)
        assert is_title_used("existing title") is True
        assert is_title_used("EXISTING TITLE") is True

    def test_strips_whitespace(self, patched_history_path):
        os.makedirs(os.path.dirname(patched_history_path), exist_ok=True)
        with open(patched_history_path, "w", encoding="utf-8") as f:
            json.dump([{"title": "Existing Title", "thread_id": "", "source": "threads", "created_at": 1000}], f)
        assert is_title_used("  Existing Title  ") is True

    def test_returns_false_for_different_title(self, patched_history_path):
        os.makedirs(os.path.dirname(patched_history_path), exist_ok=True)
        with open(patched_history_path, "w", encoding="utf-8") as f:
            json.dump([{"title": "Existing Title", "thread_id": "", "source": "threads", "created_at": 1000}], f)
        assert is_title_used("Completely Different") is False


# ===================================================================
# save_title
# ===================================================================


class TestSaveTitle:
    def test_save_new_title(self, patched_history_path):
        save_title("New Video Title", thread_id="abc123", source="threads")
        with open(patched_history_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["title"] == "New Video Title"
        assert data[0]["thread_id"] == "abc123"
        assert data[0]["source"] == "threads"
        assert "created_at" in data[0]

    def test_skip_empty_title(self, patched_history_path):
        save_title("", thread_id="abc")
        save_title("   ", thread_id="abc")
        # File should not be created or should remain empty
        if os.path.exists(patched_history_path):
            with open(patched_history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert len(data) == 0

    def test_skip_duplicate_title(self, patched_history_path):
        save_title("Unique Title", thread_id="1")
        save_title("Unique Title", thread_id="2")  # duplicate
        with open(patched_history_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1

    def test_save_multiple_unique_titles(self, patched_history_path):
        save_title("Title One", thread_id="1")
        save_title("Title Two", thread_id="2")
        save_title("Title Three", thread_id="3")
        with open(patched_history_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3


# ===================================================================
# get_title_count
# ===================================================================


class TestGetTitleCount:
    def test_zero_on_empty(self, patched_history_path):
        assert get_title_count() == 0

    def test_correct_count(self, patched_history_path):
        save_title("A", thread_id="1")
        save_title("B", thread_id="2")
        assert get_title_count() == 2
