"""
Title History - Lưu và kiểm tra các title đã được sử dụng để tránh trùng lặp.

Lưu trữ danh sách title đã tạo video vào file JSON.
Khi chọn thread mới, kiểm tra xem title đã được sử dụng chưa.
"""

import json
import os
import time
from typing import Optional

from utils.console import print_substep

TITLE_HISTORY_PATH = "./video_creation/data/title_history.json"


def _ensure_file_exists() -> None:
    """Tạo file title_history.json nếu chưa tồn tại."""
    os.makedirs(os.path.dirname(TITLE_HISTORY_PATH), exist_ok=True)
    if not os.path.exists(TITLE_HISTORY_PATH):
        with open(TITLE_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_title_history() -> list:
    """Đọc danh sách title đã sử dụng.

    Returns:
        Danh sách các dict chứa thông tin title đã dùng.
    """
    _ensure_file_exists()
    try:
        with open(TITLE_HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def is_title_used(title: str) -> bool:
    """Kiểm tra xem title đã được sử dụng chưa.

    So sánh bằng cách chuẩn hóa (lowercase, strip) để tránh trùng lặp
    do khác biệt chữ hoa/thường hoặc khoảng trắng.

    Args:
        title: Title cần kiểm tra.

    Returns:
        True nếu title đã được sử dụng, False nếu chưa.
    """
    if not title or not title.strip():
        return False

    history = load_title_history()
    normalized_title = title.strip().lower()

    for entry in history:
        saved_title = entry.get("title", "").strip().lower()
        if saved_title == normalized_title:
            return True

    return False


def save_title(title: str, thread_id: str = "", source: str = "threads") -> None:
    """Lưu title đã sử dụng vào lịch sử.

    Args:
        title: Title của video đã tạo.
        thread_id: ID của thread (để tham chiếu).
        source: Nguồn nội dung (threads/reddit).
    """
    if not title or not title.strip():
        return

    _ensure_file_exists()

    history = load_title_history()

    # Kiểm tra trùng trước khi lưu
    normalized_title = title.strip().lower()
    for entry in history:
        if entry.get("title", "").strip().lower() == normalized_title:
            print_substep(f"Title đã tồn tại trong lịch sử, bỏ qua: {title[:50]}...", style="dim")
            return

    entry = {
        "title": title.strip(),
        "thread_id": thread_id,
        "source": source,
        "created_at": int(time.time()),
    }
    history.append(entry)

    with open(TITLE_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    print_substep(f"Đã lưu title vào lịch sử: {title[:50]}...", style="bold green")


def get_title_count() -> int:
    """Đếm số title đã sử dụng.

    Returns:
        Số lượng title trong lịch sử.
    """
    return len(load_title_history())
