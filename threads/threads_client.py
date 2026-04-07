"""
Threads API Client - Lấy nội dung từ Meta Threads cho thị trường Việt Nam.

Meta Threads API sử dụng Graph API endpoint.
Docs: https://developers.facebook.com/docs/threads
"""

import re
import time as _time
from typing import Dict, List, Optional

import requests

from utils import settings
from utils.console import print_step, print_substep
from utils.title_history import is_title_used
from utils.videos import check_done
from utils.voice import sanitize_text

THREADS_API_BASE = "https://graph.threads.net/v1.0"

# Retry configuration for transient failures
_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 2
_REQUEST_TIMEOUT_SECONDS = 30


class ThreadsAPIError(Exception):
    """Lỗi khi gọi Threads API (token hết hạn, quyền thiếu, v.v.)."""

    def __init__(self, message: str, error_type: str = "", error_code: int = 0):
        self.error_type = error_type
        self.error_code = error_code
        super().__init__(message)


class ThreadsClient:
    """Client để tương tác với Threads API (Meta)."""

    def __init__(self):
        self.access_token = settings.config["threads"]["creds"]["access_token"]
        self.user_id = settings.config["threads"]["creds"]["user_id"]
        self.session = requests.Session()

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request to the Threads API with retry logic.

        Raises:
            ThreadsAPIError: If the API returns an error in the response body.
            requests.HTTPError: If the HTTP request fails after retries.
        """
        url = f"{THREADS_API_BASE}/{endpoint}"
        if params is None:
            params = {}
        params["access_token"] = self.access_token

        last_exception: Optional[Exception] = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self.session.get(url, params=params, timeout=_REQUEST_TIMEOUT_SECONDS)

                # Check for HTTP-level errors with detailed messages
                if response.status_code == 401:
                    raise ThreadsAPIError(
                        "Access token không hợp lệ hoặc đã hết hạn (HTTP 401). "
                        "Vui lòng cập nhật access_token trong config.toml.",
                        error_type="OAuthException",
                        error_code=401,
                    )
                if response.status_code == 403:
                    raise ThreadsAPIError(
                        "Không có quyền truy cập (HTTP 403). Kiểm tra quyền "
                        "threads_basic_read trong Meta Developer Portal.",
                        error_type="PermissionError",
                        error_code=403,
                    )
                response.raise_for_status()
                data = response.json()

                # Meta Graph API có thể trả về 200 nhưng body chứa error
                if "error" in data:
                    err = data["error"]
                    error_msg = err.get("message", "Unknown API error")
                    error_type = err.get("type", "")
                    error_code = err.get("code", 0)
                    raise ThreadsAPIError(
                        f"Threads API error: {error_msg} (type={error_type}, code={error_code})",
                        error_type=error_type,
                        error_code=error_code,
                    )

                return data

            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exception = exc
                if attempt < _MAX_RETRIES:
                    print_substep(
                        f"Lỗi kết nối (lần {attempt}/{_MAX_RETRIES}), "
                        f"thử lại sau {_RETRY_DELAY_SECONDS}s...",
                        style="bold yellow",
                    )
                    _time.sleep(_RETRY_DELAY_SECONDS)
                    continue
                raise
            except (ThreadsAPIError, requests.HTTPError):
                raise

    def validate_token(self) -> dict:
        """Kiểm tra access token có hợp lệ bằng cách gọi /me endpoint.

        Returns:
            User profile data nếu token hợp lệ.

        Raises:
            ThreadsAPIError: Nếu token không hợp lệ hoặc đã hết hạn.
        """
        try:
            return self._get("me", params={"fields": "id,username"})
        except (ThreadsAPIError, requests.HTTPError) as exc:
            raise ThreadsAPIError(
                "Access token không hợp lệ hoặc đã hết hạn. "
                "Vui lòng cập nhật access_token trong config.toml. "
                "Hướng dẫn: https://developers.facebook.com/docs/threads/get-started\n"
                f"Chi tiết: {exc}"
            ) from exc

    def refresh_token(self) -> str:
        """Làm mới access token (long-lived token).

        Meta Threads API cho phép refresh long-lived tokens.
        Endpoint: GET /refresh_access_token?grant_type=th_refresh_token&access_token=...

        Returns:
            Access token mới.

        Raises:
            ThreadsAPIError: Nếu không thể refresh token.
        """
        try:
            url = f"{THREADS_API_BASE}/refresh_access_token"
            response = self.session.get(
                url,
                params={
                    "grant_type": "th_refresh_token",
                    "access_token": self.access_token,
                },
                timeout=_REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                raise ThreadsAPIError(f"Không thể refresh token: {error_msg}")

            new_token = data.get("access_token", "")
            if not new_token:
                raise ThreadsAPIError("API không trả về access_token mới khi refresh.")

            self.access_token = new_token
            print_substep("✅ Đã refresh access token thành công!", style="bold green")
            return new_token
        except requests.RequestException as exc:
            raise ThreadsAPIError(
                "Không thể refresh token. Vui lòng lấy token mới từ "
                "Meta Developer Portal.\n"
                f"Chi tiết: {exc}"
            ) from exc

    def get_user_threads(self, user_id: Optional[str] = None, limit: int = 25) -> List[dict]:
        """Lấy danh sách threads của user.

        Args:
            user_id: Threads user ID. Mặc định là user đã cấu hình.
            limit: Số lượng threads tối đa cần lấy.

        Returns:
            Danh sách các thread objects.
        """
        uid = user_id or self.user_id
        data = self._get(
            f"{uid}/threads",
            params={
                "fields": "id,media_type,media_url,permalink,text,timestamp,username,shortcode,is_reply,reply_audience",
                "limit": limit,
            },
        )
        return data.get("data", [])

    def get_thread_replies(self, thread_id: str, limit: int = 50) -> List[dict]:
        """Lấy replies (comments) của một thread.

        Args:
            thread_id: ID của thread.
            limit: Số lượng replies tối đa.

        Returns:
            Danh sách replies.
        """
        data = self._get(
            f"{thread_id}/replies",
            params={
                "fields": "id,text,timestamp,username,permalink,hide_status",
                "limit": limit,
                "reverse": "true",
            },
        )
        return data.get("data", [])

    def get_thread_by_id(self, thread_id: str) -> dict:
        """Lấy thông tin chi tiết của một thread.

        Args:
            thread_id: ID của thread.

        Returns:
            Thread object.
        """
        return self._get(
            thread_id,
            params={
                "fields": "id,media_type,media_url,permalink,text,timestamp,username,shortcode",
            },
        )

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


def _get_trending_content(
    max_comment_length: int,
    min_comment_length: int,
) -> Optional[dict]:
    """Lấy nội dung từ Trending now trên Threads.

    Sử dụng Playwright scraper để lấy bài viết từ trending topics.
    Trả về None nếu không thể lấy trending content (để fallback sang user threads).
    """
    from threads.trending import (
        TrendingScrapeError,
        get_trending_threads,
        scrape_thread_replies,
    )

    try:
        trending_threads = get_trending_threads()
    except TrendingScrapeError as e:
        print_substep(f"⚠️ Lỗi lấy trending: {e}", style="bold yellow")
        return None

    if not trending_threads:
        return None

    # Chọn thread phù hợp (chưa tạo video, không chứa từ bị chặn)
    thread = None
    for t in trending_threads:
        text = t.get("text", "")
        if not text or _contains_blocked_words(text):
            continue
        title_candidate = text[:200]
        if is_title_used(title_candidate):
            print_substep(
                f"Bỏ qua trending đã tạo video: {text[:50]}...",
                style="bold yellow",
            )
            continue
        thread = t
        break

    if thread is None:
        if trending_threads:
            thread = trending_threads[0]
        else:
            return None

    thread_text = thread.get("text", "")
    thread_username = thread.get("username", "unknown")
    thread_url = thread.get("permalink", "")
    shortcode = thread.get("shortcode", "")
    topic_title = thread.get("topic_title", "")

    # Dùng topic_title làm tiêu đề video nếu có
    display_title = topic_title if topic_title else thread_text[:200]

    print_substep(
        f"Video sẽ được tạo từ trending: {display_title[:100]}...",
        style="bold green",
    )
    print_substep(f"Thread URL: {thread_url}", style="bold green")
    print_substep(f"Tác giả: @{thread_username}", style="bold blue")

    content: dict = {
        "thread_url": thread_url,
        "thread_title": display_title[:200],
        "thread_id": re.sub(r"[^\w\s-]", "", shortcode or thread_text[:20]),
        "thread_author": f"@{thread_username}",
        "is_nsfw": False,
        "thread_post": thread_text,
        "comments": [],
    }

    if not settings.config["settings"].get("storymode", False):
        # Lấy replies bằng scraping (vì thread không thuộc user nên API không dùng được)
        try:
            if thread_url:
                raw_replies = scrape_thread_replies(thread_url, limit=50)
            else:
                raw_replies = []
        except Exception as exc:
            print_substep(
                f"⚠️ Lỗi lấy replies trending: {exc}", style="bold yellow"
            )
            raw_replies = []

        for idx, reply in enumerate(raw_replies):
            reply_text = reply.get("text", "")
            reply_username = reply.get("username", "unknown")

            if not reply_text or _contains_blocked_words(reply_text):
                continue

            sanitised = sanitize_text(reply_text)
            if not sanitised or sanitised.strip() == "":
                continue

            if len(reply_text) > max_comment_length:
                continue
            if len(reply_text) < min_comment_length:
                continue

            content["comments"].append(
                {
                    "comment_body": reply_text,
                    "comment_url": "",
                    "comment_id": re.sub(
                        r"[^\w\s-]", "", f"trending_reply_{idx}"
                    ),
                    "comment_author": f"@{reply_username}",
                }
            )

    print_substep(
        f"Đã lấy nội dung trending thành công! "
        f"({len(content.get('comments', []))} replies)",
        style="bold green",
    )
    return content


def get_threads_posts(POST_ID: str = None) -> dict:
    """Lấy nội dung từ Threads để tạo video.

    Tương tự get_subreddit_threads() nhưng cho Threads.

    Args:
        POST_ID: ID cụ thể của thread. Nếu None, lấy thread mới nhất phù hợp.

    Returns:
        Dict chứa thread content và replies.

    Raises:
        ThreadsAPIError: Nếu token không hợp lệ hoặc API trả về lỗi.
        ValueError: Nếu không tìm thấy threads phù hợp.
    """
    print_substep("Đang kết nối với Threads API...")

    client = ThreadsClient()
    content = {}

    # Bước 0: Validate token trước khi gọi API
    print_substep("Đang kiểm tra access token...")
    try:
        user_info = client.validate_token()
        print_substep(
            f"✅ Token hợp lệ - User: @{user_info.get('username', 'N/A')} "
            f"(ID: {user_info.get('id', 'N/A')})",
            style="bold green",
        )
    except ThreadsAPIError:
        # Token không hợp lệ → thử refresh
        print_substep(
            "⚠️ Token có thể đã hết hạn, đang thử refresh...",
            style="bold yellow",
        )
        try:
            client.refresh_token()
            user_info = client.validate_token()
            print_substep(
                f"✅ Token đã refresh - User: @{user_info.get('username', 'N/A')}",
                style="bold green",
            )
        except (ThreadsAPIError, requests.RequestException) as refresh_err:
            print_substep(
                "❌ Không thể xác thực hoặc refresh token.\n"
                "   Vui lòng lấy token mới từ Meta Developer Portal:\n"
                "   https://developers.facebook.com/docs/threads/get-started",
                style="bold red",
            )
            raise ThreadsAPIError(
                "Access token không hợp lệ hoặc đã hết hạn. "
                "Vui lòng cập nhật access_token trong config.toml. "
                f"Chi tiết: {refresh_err}"
            ) from refresh_err

    thread_config = settings.config["threads"]["thread"]
    max_comment_length = int(thread_config.get("max_comment_length", 500))
    min_comment_length = int(thread_config.get("min_comment_length", 1))
    min_comments = int(thread_config.get("min_comments", 5))
    source = thread_config.get("source", "user")

    print_step("Đang lấy nội dung từ Threads...")

    # ------------------------------------------------------------------
    # Source: trending  –  Lấy bài viết từ Trending now
    # ------------------------------------------------------------------
    if source == "trending" and not POST_ID:
        content = _get_trending_content(
            max_comment_length=max_comment_length,
            min_comment_length=min_comment_length,
        )
        if content is not None:
            return content
        # Fallback: nếu trending thất bại, tiếp tục dùng user threads
        print_substep(
            "⚠️ Trending không khả dụng, chuyển sang lấy từ user threads...",
            style="bold yellow",
        )

    # ------------------------------------------------------------------
    # Source: user  (mặc định) hoặc POST_ID cụ thể
    # ------------------------------------------------------------------
    if POST_ID:
        # Lấy thread cụ thể theo ID
        thread = client.get_thread_by_id(POST_ID)
    else:
        # Lấy threads mới nhất và chọn thread phù hợp
        target_user = thread_config.get("target_user_id", "") or client.user_id
        threads_list = client.get_user_threads(user_id=target_user, limit=25)

        if not threads_list:
            print_substep(
                "❌ Không tìm thấy threads nào!\n"
                "   Kiểm tra các nguyên nhân sau:\n"
                f"   - User ID đang dùng: {target_user}\n"
                "   - User này có bài viết công khai không?\n"
                "   - Token có quyền threads_basic_read?\n"
                "   - Token có đúng cho user_id này không?",
                style="bold red",
            )
            raise ValueError(
                f"No threads found for user '{target_user}'. "
                "Verify the user has public posts and the access token has "
                "'threads_basic_read' permission."
            )

        # Lọc theo từ khóa nếu có
        keywords = thread_config.get("keywords", "")
        unfiltered_count = len(threads_list)
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
            filtered = client.search_threads_by_keyword(threads_list, keyword_list)
            if filtered:
                threads_list = filtered
            else:
                # Nếu keyword filter loại hết → bỏ qua filter, dùng list gốc
                print_substep(
                    f"⚠️ Keyword filter ({keywords}) loại hết {unfiltered_count} "
                    "threads. Bỏ qua keyword filter, dùng tất cả threads.",
                    style="bold yellow",
                )

        # Chọn thread phù hợp (chưa tạo video, đủ replies, title chưa dùng)
        thread = None
        for t in threads_list:
            thread_id = t.get("id", "")
            # Kiểm tra xem đã tạo video cho thread này chưa
            text = t.get("text", "")
            if not text or _contains_blocked_words(text):
                continue
            # Kiểm tra title đã được sử dụng chưa (tránh trùng lặp)
            title_candidate = text[:200] if len(text) > 200 else text
            if is_title_used(title_candidate):
                print_substep(
                    f"Bỏ qua thread đã tạo video: {text[:50]}...",
                    style="bold yellow",
                )
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
    thread_url = thread.get(
        "permalink", f"https://www.threads.net/post/{thread.get('shortcode', '')}"
    )
    thread_username = thread.get("username", "unknown")

    print_substep(f"Video sẽ được tạo từ: {thread_text[:100]}...", style="bold green")
    print_substep(f"Thread URL: {thread_url}", style="bold green")
    print_substep(f"Tác giả: @{thread_username}", style="bold blue")

    content = {}
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

            content["comments"].append(
                {
                    "comment_body": reply_text,
                    "comment_url": reply.get("permalink", ""),
                    "comment_id": re.sub(r"[^\w\s-]", "", reply.get("id", "")),
                    "comment_author": f"@{reply_username}",
                }
            )

    print_substep(
        f"Đã lấy nội dung từ Threads thành công! ({len(content.get('comments', []))} replies)",
        style="bold green",
    )
    return content
