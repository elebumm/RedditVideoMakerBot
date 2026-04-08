"""
Unit tests for utils/cleanup.py — Temporary asset cleanup.
"""

import os
import shutil

import pytest

from utils.cleanup import cleanup


class TestCleanup:
    def test_deletes_existing_directory(self, tmp_path, monkeypatch):
        # Create the directory structure that cleanup expects
        target_dir = tmp_path / "assets" / "temp" / "test_id"
        target_dir.mkdir(parents=True)
        (target_dir / "file1.mp3").write_text("audio")
        (target_dir / "file2.png").write_text("image")

        # cleanup uses relative paths "../assets/temp/{id}/"
        # so we need to run from a subdirectory context
        monkeypatch.chdir(tmp_path / "assets")
        result = cleanup("test_id")
        assert result == 1
        assert not target_dir.exists()

    def test_returns_none_for_missing_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = cleanup("nonexistent_id")
        assert result is None
