"""
Threads API Client - Lấy nội dung từ Meta Threads cho thị trường Việt Nam.

Meta Threads API sử dụng Graph API endpoint.
Docs: https://developers.facebook.com/docs/threads
"""

import re
from typing import Dict, List, Optional

import requests

from utils import settings
from utils.console import print_step, print_substep
from utils.videos import check_done
from utils.voice import sanitize_text


THREADS_API_BASE = "https://graph.threads.net/v1.0"


class ThreadsClient:
    """Client để tương tác với Threads API (Meta)."""

    def __init__(self):
        self.access_token = settings.config["threads"]["creds"]["access_token"]
        self.user_id = settings.config["threads"]["creds"]["user_id"]
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
        })

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request to the Threads API."""
        url = f"{THREADS_API_BASE}/{endpoint}"
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_user_threads(self, user_id: Optional[str] = None, limit: int = 25) -> List[dict]:
        """Lấy danh sách threads của user.

        Args:
            user_id: Threads user ID. Mặc định là user đã cấu hình.
            limit: Số lượng threads tối đa cần lấy.

        Returns:
            Danh sách các thread objects.
        """
        uid = user_id or self.user_id
        data = self._get(f"{uid}/threads", params={
            "fields": "id,media_type,media_url,permalink,text,timestamp,username,shortcode,is_reply,reply_audience",
            "limit": limit,
        })
        return data.get("data", [])

    def get_thread_replies(self, thread_id: str, limit: int = 50) -> List[dict]:
        """Lấy replies (comments) của một thread.

        Args:
            thread_id: ID của thread.
            limit: Số lượng replies tối đa.

        Returns:
            Danh sách replies.
        """
        data = self._get(f"{thread_id}/replies", params={
            "fields": "id,text,timestamp,username,permalink,hide_status",
            "limit": limit,
            "reverse": "true",
        })
        return data.get("data", [])

    def get_thread_by_id(self, thread_id: str) -> dict:
        """Lấy thông tin chi tiết của một thread.

        Args:
            thread_id: ID của thread.

        Returns:
            Thread object.
        """
        return self._get(thread_id, params={
            "fields": "id,media_type,media_url,permalink,text,timestamp,username,shortcode",
        })

    def search_threads_by_keyword(self, threads: List[dict], keywords: List[str]) -> List[dict]:
        """Lọc threads theo từ khóa.

        Args:
            threads: Danh sách threads.
            keywords: Danh sách từ khóa cần tìm.

        Returns:
            Danh sách threads chứa từ khóa.
        """
        filtered = []
        for thread in threads:
            text = thread.get("text", "").lower()
            for keyword in keywords:
                if keyword.lower() in text:
                    filtered.append(thread)
                    break
        return filtered


def _contains_blocked_words(text: str) -> bool:
    """Kiểm tra xem text có chứa từ bị chặn không."""
    blocked_words = settings.config["threads"]["thread"].get("blocked_words", "")
    if not blocked_words:
        return False
    blocked_list = [w.strip().lower() for w in blocked_words.split(",") if w.strip()]
    text_lower = text.lower()
    return any(word in text_lower for word in blocked_list)


def get_threads_posts(POST_ID: str = None) -> dict:
    """Lấy nội dung từ Threads để tạo video.

    Tương tự get_subreddit_threads() nhưng cho Threads.

    Args:
        POST_ID: ID cụ thể của thread. Nếu None, lấy thread mới nhất phù hợp.

    Returns:
        Dict chứa thread content và replies.
    """
    print_substep("Đang kết nối với Threads API...")

    client = ThreadsClient()
    content = {}

    thread_config = settings.config["threads"]["thread"]
    max_comment_length = int(thread_config.get("max_comment_length", 500))
    min_comment_length = int(thread_config.get("min_comment_length", 1))
    min_comments = int(thread_config.get("min_comments", 5))

    print_step("Đang lấy nội dung từ Threads...")

    if POST_ID:
        # Lấy thread cụ thể theo ID
        thread = client.get_thread_by_id(POST_ID)
    else:
        # Lấy threads mới nhất và chọn thread phù hợp
        target_user = thread_config.get("target_user_id", "") or client.user_id
        threads_list = client.get_user_threads(user_id=target_user, limit=25)

        if not threads_list:
            print_substep("Không tìm thấy threads nào!", style="bold red")
            raise ValueError("No threads found")

        # Lọc theo từ khóa nếu có
        keywords = thread_config.get("keywords", "")
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
            threads_list = client.search_threads_by_keyword(threads_list, keyword_list)

        # Chọn thread phù hợp (chưa tạo video, đủ replies)
        thread = None
        for t in threads_list:
            thread_id = t.get("id", "")
            # Kiểm tra xem đã tạo video cho thread này chưa
            text = t.get("text", "")
            if not text or _contains_blocked_words(text):
                continue
            # Kiểm tra số lượng replies
            try:
                replies = client.get_thread_replies(thread_id, limit=min_comments + 5)
                if len(replies) >= min_comments:
                    thread = t
                    break
            except Exception:
                continue

        if thread is None:
            # Nếu không tìm được thread đủ comments, lấy thread đầu tiên
            if threads_list:
                thread = threads_list[0]
            else:
                print_substep("Không tìm thấy thread phù hợp!", style="bold red")
                raise ValueError("No suitable thread found")

    thread_id = thread.get("id", "")
    thread_text = thread.get("text", "")
    thread_url = thread.get("permalink", f"https://www.threads.net/post/{thread.get('shortcode', '')}")
    thread_username = thread.get("username", "unknown")

    print_substep(f"Video sẽ được tạo từ: {thread_text[:100]}...", style="bold green")
    print_substep(f"Thread URL: {thread_url}", style="bold green")
    print_substep(f"Tác giả: @{thread_username}", style="bold blue")

    content["thread_url"] = thread_url
    content["thread_title"] = thread_text[:200] if len(thread_text) > 200 else thread_text
    content["thread_id"] = re.sub(r"[^\w\s-]", "", thread_id)
    content["thread_author"] = f"@{thread_username}"
    content["is_nsfw"] = False
    content["thread_post"] = thread_text
    content["comments"] = []

    if settings.config["settings"].get("storymode", False):
        # Story mode - đọc toàn bộ nội dung bài viết
        content["thread_post"] = thread_text
    else:
        # Comment mode - lấy replies
        try:
            replies = client.get_thread_replies(thread_id, limit=50)
        except Exception as e:
            print_substep(f"Lỗi khi lấy replies: {e}", style="bold red")
            replies = []

        for reply in replies:
            reply_text = reply.get("text", "")
            reply_username = reply.get("username", "unknown")

            if not reply_text:
                continue
            if reply.get("hide_status", "") == "HIDDEN":
                continue
            if _contains_blocked_words(reply_text):
                continue

            sanitised = sanitize_text(reply_text)
            if not sanitised or sanitised.strip() == "":
                continue

            if len(reply_text) > max_comment_length:
                continue
            if len(reply_text) < min_comment_length:
                continue

            content["comments"].append({
                "comment_body": reply_text,
                "comment_url": reply.get("permalink", ""),
                "comment_id": re.sub(r"[^\w\s-]", "", reply.get("id", "")),
                "comment_author": f"@{reply_username}",
            })

    print_substep(
        f"Đã lấy nội dung từ Threads thành công! ({len(content.get('comments', []))} replies)",
        style="bold green",
    )
    return content
