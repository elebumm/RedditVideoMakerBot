"""
Unit tests for utils/settings.py — Safe type casting and config validation.
"""

import pytest

# Import after conftest sets up sys.path
from utils.settings import _safe_type_cast, check, crawl, crawl_and_check


# ===================================================================
# _safe_type_cast
# ===================================================================


class TestSafeTypeCast:
    """Tests for _safe_type_cast — replacement for eval() calls."""

    def test_cast_int(self):
        assert _safe_type_cast("int", "42") == 42
        assert _safe_type_cast("int", 42) == 42

    def test_cast_float(self):
        assert _safe_type_cast("float", "3.14") == pytest.approx(3.14)
        assert _safe_type_cast("float", 3) == pytest.approx(3.0)

    def test_cast_str(self):
        assert _safe_type_cast("str", 123) == "123"
        assert _safe_type_cast("str", "hello") == "hello"

    def test_cast_bool_true_variants(self):
        assert _safe_type_cast("bool", "true") is True
        assert _safe_type_cast("bool", "True") is True
        assert _safe_type_cast("bool", "1") is True
        assert _safe_type_cast("bool", "yes") is True
        assert _safe_type_cast("bool", 1) is True

    def test_cast_bool_false_variants(self):
        assert _safe_type_cast("bool", "false") is False
        assert _safe_type_cast("bool", "0") is False
        assert _safe_type_cast("bool", "no") is False
        assert _safe_type_cast("bool", 0) is False

    def test_cast_false_literal(self):
        """The special key "False" always returns False."""
        assert _safe_type_cast("False", "anything") is False
        assert _safe_type_cast("False", True) is False

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown type"):
            _safe_type_cast("list", "[1, 2]")

    def test_invalid_int_raises(self):
        with pytest.raises(ValueError):
            _safe_type_cast("int", "not_a_number")


# ===================================================================
# crawl
# ===================================================================


class TestCrawl:
    """Tests for crawl — recursive dictionary walking."""

    def test_flat_dict(self):
        collected = []
        crawl({"a": 1, "b": 2}, func=lambda path, val: collected.append((path, val)))
        assert (["a"], 1) in collected
        assert (["b"], 2) in collected

    def test_nested_dict(self):
        collected = []
        crawl(
            {"section": {"key1": "v1", "key2": "v2"}},
            func=lambda path, val: collected.append((path, val)),
        )
        assert (["section", "key1"], "v1") in collected
        assert (["section", "key2"], "v2") in collected

    def test_empty_dict(self):
        collected = []
        crawl({}, func=lambda path, val: collected.append((path, val)))
        assert collected == []


# ===================================================================
# check (with mocked handle_input to avoid interactive prompt)
# ===================================================================


class TestCheck:
    """Tests for the check function — value validation against checks dict."""

    def test_valid_value_passes(self):
        result = check(42, {"type": "int", "nmin": 0, "nmax": 100}, "test_var")
        assert result == 42

    def test_valid_string_passes(self):
        result = check("hello", {"type": "str"}, "test_var")
        assert result == "hello"

    def test_valid_options(self):
        result = check("dark", {"type": "str", "options": ["dark", "light"]}, "theme")
        assert result == "dark"

    def test_valid_regex(self):
        result = check("vi", {"type": "str", "regex": r"^[a-z]{2}$"}, "lang")
        assert result == "vi"

    def test_valid_range_min(self):
        result = check(5, {"type": "int", "nmin": 1, "nmax": 10}, "count")
        assert result == 5

    def test_boundary_nmin(self):
        result = check(1, {"type": "int", "nmin": 1, "nmax": 10}, "count")
        assert result == 1

    def test_boundary_nmax(self):
        result = check(10, {"type": "int", "nmin": 1, "nmax": 10}, "count")
        assert result == 10

    def test_string_length_check(self):
        """Iterable values check len() against nmin/nmax."""
        result = check("hello", {"type": "str", "nmin": 1, "nmax": 20}, "text")
        assert result == "hello"


# ===================================================================
# crawl_and_check
# ===================================================================


class TestCrawlAndCheck:
    """Tests for crawl_and_check — recursive config validation."""

    def test_creates_missing_path(self):
        obj = {"section": {"key": "existing"}}
        result = crawl_and_check(obj, ["section", "key"], {"type": "str"}, "test")
        assert "section" in result
        assert result["section"]["key"] == "existing"

    def test_preserves_existing_value(self):
        obj = {"section": {"key": "existing"}}
        result = crawl_and_check(obj, ["section", "key"], {"type": "str"}, "test")
        assert result["section"]["key"] == "existing"

    def test_validates_nested_int(self):
        obj = {"settings": {"count": 5}}
        result = crawl_and_check(obj, ["settings", "count"], {"type": "int", "nmin": 1, "nmax": 10}, "count")
        assert result["settings"]["count"] == 5
