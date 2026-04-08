"""
Threads API Client - Tương tác đầy đủ với Meta Threads API.

Triển khai theo tài liệu chính thức:
    https://developers.facebook.com/docs/threads

Các API được hỗ trợ:
    1. Threads Profiles API     – Lấy thông tin hồ sơ người dùng
    2. Threads Media API (Read) – Lấy threads, media objects
    3. Threads Publishing API   – Tạo & đăng bài mới (text, image, video, carousel)
    4. Threads Reply Management  – Lấy replies, conversation tree, ẩn/hiện reply
    5. Threads Insights API     – Metrics cấp thread và cấp user
    6. Rate Limiting            – Kiểm tra quota publishing
    7. Token Management         – Refresh long-lived token
"""

import re
import time as _time
from typing import Any, Dict, List, Optional

import requests

from utils import settings
from utils.console import print_step, print_substep
from utils.title_history import is_title_used
from utils.videos import check_done
from utils.voice import sanitize_text

# ---------------------------------------------------------------------------
# API base URL
# ---------------------------------------------------------------------------
THREADS_API_BASE = "https://graph.threads.net/v1.0"

# ---------------------------------------------------------------------------
# Retry / timeout configuration
# ---------------------------------------------------------------------------
_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 2
_REQUEST_TIMEOUT_SECONDS = 30

# Title length limit for video titles
_MAX_TITLE_LENGTH = 200

# ---------------------------------------------------------------------------
# Field constants  (theo Threads API docs)
# https://developers.facebook.com/docs/threads/threads-media
# ---------------------------------------------------------------------------

# Fields cho Thread Media object
THREAD_FIELDS = (
    "id,media_product_type,media_type,media_url,permalink,"
    "owner,username,text,timestamp,shortcode,thumbnail_url,"
    "children,is_quote_status,has_replies,root_post,replied_to,"
    "is_reply,is_reply_owned_by_me,hide_status,reply_audience,"
    "link_attachment_url,alt_text"
)

# Fields nhẹ hơn khi chỉ cần danh sách
THREAD_LIST_FIELDS = (
    "id,media_type,media_url,permalink,text,timestamp,"
    "username,shortcode,has_replies,is_reply,reply_audience"
)

# Fields cho Reply object
REPLY_FIELDS = (
    "id,text,username,permalink,timestamp,media_type,"
    "media_url,shortcode,has_replies,root_post,replied_to,"
    "is_reply,hide_status"
)

# Fields cho User Profile
PROFILE_FIELDS = "id,username,name,threads_profile_picture_url,threads_biography"

# Metrics cho Thread-level insights
THREAD_INSIGHT_METRICS = "views,likes,replies,reposts,quotes,shares"

# Metrics cho User-level insights
USER_INSIGHT_METRICS = "views,likes,replies,reposts,quotes,followers_count,follower_demographics"

# Trạng thái publish container
CONTAINER_STATUS_FINISHED = "FINISHED"
CONTAINER_STATUS_ERROR = "ERROR"
CONTAINER_STATUS_IN_PROGRESS = "IN_PROGRESS"

# Media types cho publishing
MEDIA_TYPE_TEXT = "TEXT"
MEDIA_TYPE_IMAGE = "IMAGE"
MEDIA_TYPE_VIDEO = "VIDEO"
MEDIA_TYPE_CAROUSEL = "CAROUSEL"

# Reply control options
REPLY_CONTROL_EVERYONE = "everyone"
REPLY_CONTROL_ACCOUNTS_YOU_FOLLOW = "accounts_you_follow"
REPLY_CONTROL_MENTIONED_ONLY = "mentioned_only"

# Polling configuration cho publishing
_PUBLISH_POLL_INTERVAL = 3  # seconds
_PUBLISH_POLL_MAX_ATTEMPTS = 40  # ~2 phút

# Engagement scoring weights cho thread selection
_SCORE_WEIGHT_VIEWS = 1
_SCORE_WEIGHT_LIKES = 5
_SCORE_WEIGHT_REPLIES = 10
_SCORE_WEIGHT_REPOSTS = 15


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ThreadsAPIError(Exception):
    """Lỗi khi gọi Threads API (token hết hạn, quyền thiếu, v.v.)."""

    def __init__(self, message: str, error_type: str = "", error_code: int = 0):
        self.error_type = error_type
        self.error_code = error_code
        super().__init__(message)


# ---------------------------------------------------------------------------
# ThreadsClient
# ---------------------------------------------------------------------------


class ThreadsClient:
    """Client đầy đủ để tương tác với Threads API (Meta).

    Docs: https://developers.facebook.com/docs/threads

    Hỗ trợ:
        - Profiles API: lấy thông tin user
        - Media API: lấy threads, thread chi tiết
        - Reply Management: replies, conversation, ẩn/hiện
        - Publishing API: tạo & đăng bài (text, image, video, carousel)
        - Insights API: metrics cấp thread & user
        - Rate Limiting: kiểm tra quota publishing
        - Token Management: validate & refresh
    """

    def __init__(self):
        self.access_token: str = settings.config["threads"]["creds"]["access_token"]
        self.user_id: str = settings.config["threads"]["creds"]["user_id"]
        self.session = requests.Session()

    # ===================================================================
    # Internal HTTP helpers
    # ===================================================================

    def _handle_api_response(self, response: requests.Response) -> dict:
        """Parse và kiểm tra response từ Threads API.

        Raises:
            ThreadsAPIError: Nếu response chứa lỗi.
        """
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
                "threads_basic trong Meta Developer Portal.",
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

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """GET request tới Threads API với retry logic.

        Raises:
            ThreadsAPIError: Nếu API trả về lỗi.
            requests.HTTPError: Nếu HTTP request thất bại sau retries.
        """
        url = f"{THREADS_API_BASE}/{endpoint}"
        if params is None:
            params = {}
        params["access_token"] = self.access_token

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self.session.get(
                    url, params=params, timeout=_REQUEST_TIMEOUT_SECONDS
                )
                return self._handle_api_response(response)

            except (requests.ConnectionError, requests.Timeout) as exc:
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

        # Unreachable, but satisfies type checkers
        raise ThreadsAPIError("Unexpected: all retries exhausted without result")

    def _post(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """POST request tới Threads API với retry logic.

        Dùng cho Publishing API (tạo container, publish, manage reply).

        Raises:
            ThreadsAPIError: Nếu API trả về lỗi.
            requests.HTTPError: Nếu HTTP request thất bại sau retries.
        """
        url = f"{THREADS_API_BASE}/{endpoint}"
        if data is None:
            data = {}
        data["access_token"] = self.access_token

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self.session.post(
                    url, data=data, timeout=_REQUEST_TIMEOUT_SECONDS
                )
                return self._handle_api_response(response)

            except (requests.ConnectionError, requests.Timeout) as exc:
                if attempt < _MAX_RETRIES:
                    print_substep(
                        f"Lỗi kết nối POST (lần {attempt}/{_MAX_RETRIES}), "
                        f"thử lại sau {_RETRY_DELAY_SECONDS}s...",
                        style="bold yellow",
                    )
                    _time.sleep(_RETRY_DELAY_SECONDS)
                    continue
                raise
            except (ThreadsAPIError, requests.HTTPError):
                raise

        raise ThreadsAPIError("Unexpected: all retries exhausted without result")

    def _get_paginated(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        max_items: int = 100,
    ) -> List[dict]:
        """GET request với auto-pagination qua cursor.

        Threads API sử dụng cursor-based pagination:
        ``paging.cursors.after`` / ``paging.next``

        Args:
            endpoint: API endpoint.
            params: Query parameters.
            max_items: Số items tối đa cần lấy.

        Returns:
            Danh sách tất cả items qua các trang.
        """
        all_items: List[dict] = []
        if params is None:
            params = {}

        while len(all_items) < max_items:
            remaining = max_items - len(all_items)
            params["limit"] = min(remaining, 100)  # API max 100/page

            data = self._get(endpoint, params=dict(params))
            items = data.get("data", [])
            all_items.extend(items)

            if not items:
                break

            # Kiểm tra có trang tiếp theo không
            paging = data.get("paging", {})
            next_cursor = paging.get("cursors", {}).get("after")
            if not next_cursor or "next" not in paging:
                break

            params["after"] = next_cursor

        return all_items[:max_items]

    # ===================================================================
    # 1. Token Management
    # https://developers.facebook.com/docs/threads/get-started
    # ===================================================================

    def validate_token(self) -> dict:
        """Kiểm tra access token bằng /me endpoint.

        Returns:
            User profile data (id, username, name, ...).

        Raises:
            ThreadsAPIError: Nếu token không hợp lệ hoặc đã hết hạn.
        """
        try:
            return self._get("me", params={"fields": PROFILE_FIELDS})
        except (ThreadsAPIError, requests.HTTPError) as exc:
            raise ThreadsAPIError(
                "Access token không hợp lệ hoặc đã hết hạn. "
                "Vui lòng cập nhật access_token trong config.toml. "
                "Hướng dẫn: https://developers.facebook.com/docs/threads/get-started\n"
                f"Chi tiết: {exc}"
            ) from exc

    def refresh_token(self) -> str:
        """Làm mới long-lived access token.

        Endpoint: GET /refresh_access_token?grant_type=th_refresh_token
        Docs: https://developers.facebook.com/docs/threads/get-started#refresh-long-lived-token

        Lưu ý:
            - Chỉ long-lived tokens mới refresh được.
            - Short-lived tokens cần đổi sang long-lived trước.
            - Token phải chưa hết hạn để refresh.

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
                raise ThreadsAPIError(
                    "API không trả về access_token mới khi refresh."
                )

            self.access_token = new_token
            # Cập nhật config in-memory để các module khác dùng token mới
            settings.config["threads"]["creds"]["access_token"] = new_token
            print_substep(
                "✅ Đã refresh access token thành công!", style="bold green"
            )
            return new_token
        except requests.RequestException as exc:
            raise ThreadsAPIError(
                "Không thể refresh token. Vui lòng lấy token mới từ "
                "Meta Developer Portal.\n"
                f"Chi tiết: {exc}"
            ) from exc

    # ===================================================================
    # 2. Threads Profiles API
    # https://developers.facebook.com/docs/threads/threads-profiles
    # ===================================================================

    def get_user_profile(self, user_id: Optional[str] = None) -> dict:
        """Lấy thông tin hồ sơ người dùng.

        Fields: id, username, name, threads_profile_picture_url, threads_biography

        Args:
            user_id: Threads user ID. Dùng ``"me"`` hoặc None cho user hiện tại.

        Returns:
            Dict chứa thông tin profile.
        """
        uid = user_id or "me"
        return self._get(uid, params={"fields": PROFILE_FIELDS})

    # ===================================================================
    # 3. Threads Media API (Read)
    # https://developers.facebook.com/docs/threads/threads-media
    # ===================================================================

    def get_user_threads(
        self,
        user_id: Optional[str] = None,
        limit: int = 25,
        fields: Optional[str] = None,
    ) -> List[dict]:
        """Lấy danh sách threads của user.

        Endpoint: GET /{user-id}/threads
        Docs: https://developers.facebook.com/docs/threads/threads-media#get-threads

        Args:
            user_id: Threads user ID. Mặc định là user đã cấu hình.
            limit: Số lượng threads tối đa (max 100).
            fields: Custom fields. Mặc định dùng THREAD_LIST_FIELDS.

        Returns:
            Danh sách thread objects.
        """
        uid = user_id or self.user_id
        return self._get_paginated(
            f"{uid}/threads",
            params={"fields": fields or THREAD_LIST_FIELDS},
            max_items=limit,
        )

    def get_thread_by_id(
        self,
        thread_id: str,
        fields: Optional[str] = None,
    ) -> dict:
        """Lấy thông tin chi tiết của một thread.

        Endpoint: GET /{thread-media-id}
        Docs: https://developers.facebook.com/docs/threads/threads-media#get-single-thread

        Fields đầy đủ: id, media_product_type, media_type, media_url,
        permalink, owner, username, text, timestamp, shortcode,
        thumbnail_url, children, is_quote_status, has_replies,
        root_post, replied_to, is_reply, is_reply_owned_by_me,
        hide_status, reply_audience, link_attachment_url, alt_text

        Args:
            thread_id: Media ID của thread.
            fields: Custom fields. Mặc định dùng THREAD_FIELDS (đầy đủ).

        Returns:
            Thread object.
        """
        return self._get(
            thread_id,
            params={"fields": fields or THREAD_FIELDS},
        )

    def get_user_replies(
        self,
        user_id: Optional[str] = None,
        limit: int = 25,
        fields: Optional[str] = None,
    ) -> List[dict]:
        """Lấy danh sách replies mà user đã đăng.

        Endpoint: GET /{user-id}/replies
        Docs: https://developers.facebook.com/docs/threads/reply-management#get-user-replies

        Args:
            user_id: Threads user ID. Mặc định là user đã cấu hình.
            limit: Số lượng replies tối đa.
            fields: Custom fields.

        Returns:
            Danh sách reply objects.
        """
        uid = user_id or self.user_id
        return self._get_paginated(
            f"{uid}/replies",
            params={"fields": fields or REPLY_FIELDS},
            max_items=limit,
        )

    # ===================================================================
    # 4. Threads Reply Management API
    # https://developers.facebook.com/docs/threads/reply-management
    # ===================================================================

    def get_thread_replies(
        self,
        thread_id: str,
        limit: int = 50,
        fields: Optional[str] = None,
        reverse: bool = True,
    ) -> List[dict]:
        """Lấy replies trực tiếp (top-level) của một thread.

        Endpoint: GET /{thread-media-id}/replies
        Docs: https://developers.facebook.com/docs/threads/reply-management#get-replies

        Lưu ý: Chỉ trả về replies trực tiếp (1 cấp).
        Dùng ``get_conversation()`` để lấy toàn bộ conversation tree.

        Args:
            thread_id: Media ID của thread.
            limit: Số lượng replies tối đa.
            fields: Custom fields. Mặc định dùng REPLY_FIELDS.
            reverse: ``True`` để sắp xếp cũ nhất trước (chronological).

        Returns:
            Danh sách reply objects.
        """
        params: Dict[str, Any] = {
            "fields": fields or REPLY_FIELDS,
        }
        if reverse:
            params["reverse"] = "true"

        return self._get_paginated(
            f"{thread_id}/replies",
            params=params,
            max_items=limit,
        )

    def get_conversation(
        self,
        thread_id: str,
        limit: int = 100,
        fields: Optional[str] = None,
        reverse: bool = True,
    ) -> List[dict]:
        """Lấy toàn bộ conversation tree của một thread.

        Endpoint: GET /{thread-media-id}/conversation
        Docs: https://developers.facebook.com/docs/threads/reply-management#get-conversation

        Trả về tất cả replies ở mọi cấp (nested replies) trong cùng
        conversation, không chỉ top-level.

        Args:
            thread_id: Media ID của thread gốc.
            limit: Số lượng items tối đa.
            fields: Custom fields. Mặc định dùng REPLY_FIELDS.
            reverse: ``True`` để sắp xếp cũ nhất trước.

        Returns:
            Danh sách tất cả reply objects trong conversation.
        """
        params: Dict[str, Any] = {
            "fields": fields or REPLY_FIELDS,
        }
        if reverse:
            params["reverse"] = "true"

        return self._get_paginated(
            f"{thread_id}/conversation",
            params=params,
            max_items=limit,
        )

    def manage_reply(self, reply_id: str, hide: bool = True) -> dict:
        """Ẩn hoặc hiện một reply.

        Endpoint: POST /{reply-id}/manage_reply
        Docs: https://developers.facebook.com/docs/threads/reply-management#hide-replies

        Chỉ hoạt động với replies trên threads mà user sở hữu.

        Args:
            reply_id: Media ID của reply.
            hide: ``True`` để ẩn, ``False`` để hiện lại.

        Returns:
            Response dict (``{"success": true}``).
        """
        return self._post(
            f"{reply_id}/manage_reply",
            data={"hide": str(hide).lower()},
        )

    # ===================================================================
    # 5. Threads Publishing API
    # https://developers.facebook.com/docs/threads/posts
    # ===================================================================

    def create_container(
        self,
        media_type: str = MEDIA_TYPE_TEXT,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        children: Optional[List[str]] = None,
        reply_to_id: Optional[str] = None,
        reply_control: Optional[str] = None,
        link_attachment: Optional[str] = None,
        quote_post_id: Optional[str] = None,
        alt_text: Optional[str] = None,
        allowlisted_country_codes: Optional[List[str]] = None,
    ) -> str:
        """Tạo media container (bước 1 của publishing flow).

        Endpoint: POST /{user-id}/threads
        Docs: https://developers.facebook.com/docs/threads/posts#create-container

        Publishing flow: create_container() → publish_thread()

        Args:
            media_type: Loại media (TEXT, IMAGE, VIDEO, CAROUSEL).
            text: Nội dung text (tối đa 500 ký tự). Bắt buộc cho TEXT.
            image_url: URL hình ảnh công khai. Bắt buộc cho IMAGE.
            video_url: URL video công khai. Bắt buộc cho VIDEO.
            children: Danh sách container IDs cho CAROUSEL (2-20 items).
            reply_to_id: Media ID để reply (đăng reply thay vì thread mới).
            reply_control: Ai được reply: everyone, accounts_you_follow,
                          mentioned_only. Mặc định: everyone.
            link_attachment: URL đính kèm (chỉ cho TEXT posts).
            quote_post_id: Media ID của thread muốn quote.
            alt_text: Mô tả alternative cho media (accessibility).
            allowlisted_country_codes: Giới hạn quốc gia xem được post.

        Returns:
            Container ID (creation_id) để dùng trong ``publish_thread()``.

        Raises:
            ThreadsAPIError: Nếu không thể tạo container.
        """
        post_data: Dict[str, Any] = {"media_type": media_type}

        if text is not None:
            post_data["text"] = text
        if image_url is not None:
            post_data["image_url"] = image_url
        if video_url is not None:
            post_data["video_url"] = video_url
        if children is not None:
            post_data["children"] = ",".join(children)
        if reply_to_id is not None:
            post_data["reply_to_id"] = reply_to_id
        if reply_control is not None:
            post_data["reply_control"] = reply_control
        if link_attachment is not None:
            post_data["link_attachment"] = link_attachment
        if quote_post_id is not None:
            post_data["quote_post_id"] = quote_post_id
        if alt_text is not None:
            post_data["alt_text"] = alt_text
        if allowlisted_country_codes is not None:
            post_data["allowlisted_country_codes"] = ",".join(
                allowlisted_country_codes
            )

        result = self._post(f"{self.user_id}/threads", data=post_data)
        container_id = result.get("id", "")
        if not container_id:
            raise ThreadsAPIError("API không trả về container ID sau khi tạo.")
        return container_id

    def get_container_status(self, container_id: str) -> dict:
        """Kiểm tra trạng thái của media container.

        Endpoint: GET /{container-id}?fields=status,error_message
        Docs: https://developers.facebook.com/docs/threads/posts#check-status

        Status:
            - ``FINISHED``: Sẵn sàng publish.
            - ``IN_PROGRESS``: Đang xử lý (chờ thêm).
            - ``ERROR``: Lỗi, xem ``error_message``.

        Args:
            container_id: ID của container.

        Returns:
            Dict chứa ``{id, status, error_message}``.
        """
        return self._get(
            container_id,
            params={"fields": "id,status,error_message"},
        )

    def publish_thread(self, container_id: str) -> str:
        """Publish một media container đã tạo (bước 2 của publishing flow).

        Endpoint: POST /{user-id}/threads_publish
        Docs: https://developers.facebook.com/docs/threads/posts#publish-container

        Args:
            container_id: ID từ ``create_container()``.

        Returns:
            Media ID của thread đã publish.

        Raises:
            ThreadsAPIError: Nếu không thể publish.
        """
        result = self._post(
            f"{self.user_id}/threads_publish",
            data={"creation_id": container_id},
        )
        media_id = result.get("id", "")
        if not media_id:
            raise ThreadsAPIError("API không trả về media ID sau khi publish.")
        return media_id

    def create_and_publish(
        self,
        text: Optional[str] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        reply_to_id: Optional[str] = None,
        reply_control: Optional[str] = None,
        link_attachment: Optional[str] = None,
        poll_for_ready: bool = True,
    ) -> str:
        """Tiện ích: tạo container + chờ sẵn sàng + publish trong 1 bước.

        Tự động xác định media_type từ parameters:
            - Chỉ ``text`` → TEXT
            - Có ``image_url`` → IMAGE
            - Có ``video_url`` → VIDEO

        Args:
            text: Nội dung text.
            image_url: URL hình ảnh.
            video_url: URL video.
            reply_to_id: Media ID để reply.
            reply_control: Ai được reply.
            link_attachment: URL đính kèm.
            poll_for_ready: Chờ container FINISHED trước khi publish
                           (quan trọng cho IMAGE/VIDEO).

        Returns:
            Media ID của thread đã publish.

        Raises:
            ThreadsAPIError: Nếu quá trình thất bại.
        """
        # Xác định media_type
        if video_url:
            media_type = MEDIA_TYPE_VIDEO
        elif image_url:
            media_type = MEDIA_TYPE_IMAGE
        else:
            media_type = MEDIA_TYPE_TEXT

        # Bước 1: Tạo container
        container_id = self.create_container(
            media_type=media_type,
            text=text,
            image_url=image_url,
            video_url=video_url,
            reply_to_id=reply_to_id,
            reply_control=reply_control,
            link_attachment=link_attachment,
        )

        # Bước 2: Poll cho đến khi container FINISHED (cho IMAGE/VIDEO)
        if poll_for_ready and media_type != MEDIA_TYPE_TEXT:
            for attempt in range(1, _PUBLISH_POLL_MAX_ATTEMPTS + 1):
                status_data = self.get_container_status(container_id)
                status = status_data.get("status", "")

                if status == CONTAINER_STATUS_FINISHED:
                    break
                if status == CONTAINER_STATUS_ERROR:
                    error_msg = status_data.get(
                        "error_message", "Unknown publish error"
                    )
                    raise ThreadsAPIError(
                        f"Container lỗi khi xử lý media: {error_msg}"
                    )

                _time.sleep(_PUBLISH_POLL_INTERVAL)
            else:
                raise ThreadsAPIError(
                    "Timeout chờ container FINISHED. "
                    "Media có thể quá lớn hoặc format không hỗ trợ."
                )

        # Bước 3: Publish
        return self.publish_thread(container_id)

    # ===================================================================
    # 6. Threads Insights API
    # https://developers.facebook.com/docs/threads/insights
    # ===================================================================

    def get_thread_insights(
        self,
        thread_id: str,
        metrics: Optional[str] = None,
    ) -> List[dict]:
        """Lấy insights/metrics cho một thread.

        Endpoint: GET /{thread-media-id}/insights
        Docs: https://developers.facebook.com/docs/threads/insights#thread-insights

        Metrics khả dụng: views, likes, replies, reposts, quotes, shares

        Args:
            thread_id: Media ID của thread.
            metrics: Comma-separated metrics. Mặc định: tất cả.

        Returns:
            Danh sách metric objects: ``[{name, period, values, ...}]``.
        """
        data = self._get(
            f"{thread_id}/insights",
            params={"metric": metrics or THREAD_INSIGHT_METRICS},
        )
        return data.get("data", [])

    def get_thread_engagement(self, thread_id: str) -> Dict[str, int]:
        """Tiện ích: lấy engagement metrics dạng dict đơn giản.

        Returns:
            Dict ``{views: N, likes: N, replies: N, reposts: N, quotes: N, shares: N}``.
        """
        raw = self.get_thread_insights(thread_id)
        engagement: Dict[str, int] = {}
        for item in raw:
            name = item.get("name", "")
            values = item.get("values", [])
            if values:
                engagement[name] = values[0].get("value", 0)
        return engagement

    def get_user_insights(
        self,
        user_id: Optional[str] = None,
        metrics: Optional[str] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
    ) -> List[dict]:
        """Lấy insights/metrics cấp user (tổng hợp).

        Endpoint: GET /{user-id}/threads_insights
        Docs: https://developers.facebook.com/docs/threads/insights#user-insights

        Metrics: views, likes, replies, reposts, quotes,
                followers_count, follower_demographics

        Lưu ý: follower_demographics cần followers > 100.

        Args:
            user_id: Threads user ID. Mặc định là user hiện tại.
            metrics: Comma-separated metrics.
            since: Unix timestamp bắt đầu (cho time-series metrics).
            until: Unix timestamp kết thúc.

        Returns:
            Danh sách metric objects.
        """
        uid = user_id or self.user_id
        params: Dict[str, Any] = {
            "metric": metrics or USER_INSIGHT_METRICS,
        }
        if since is not None:
            params["since"] = since
        if until is not None:
            params["until"] = until

        data = self._get(f"{uid}/threads_insights", params=params)
        return data.get("data", [])

    # ===================================================================
    # 7. Rate Limiting
    # https://developers.facebook.com/docs/threads/troubleshooting#rate-limiting
    # ===================================================================

    def get_publishing_limit(
        self,
        user_id: Optional[str] = None,
    ) -> dict:
        """Kiểm tra quota publishing hiện tại.

        Endpoint: GET /{user-id}/threads_publishing_limit
        Docs: https://developers.facebook.com/docs/threads/troubleshooting#rate-limiting

        Returns:
            Dict chứa ``{quota_usage, config: {quota_total, quota_duration}}``.
            Mặc định: 250 posts / 24 giờ.
        """
        uid = user_id or self.user_id
        data = self._get(
            f"{uid}/threads_publishing_limit",
            params={"fields": "quota_usage,config"},
        )
        items = data.get("data", [])
        return items[0] if items else {}

    def can_publish(self) -> bool:
        """Kiểm tra có còn quota để publish không.

        Returns:
            ``True`` nếu còn quota, ``False`` nếu đã hết.
        """
        try:
            limit_data = self.get_publishing_limit()
            usage = limit_data.get("quota_usage", 0)
            config = limit_data.get("config", {})
            total = config.get("quota_total", 250)
            return usage < total
        except (ThreadsAPIError, requests.RequestException):
            # Nếu không lấy được limit, cho phép publish (optimistic)
            return True

    # ===================================================================
    # Utility methods (không gọi API)
    # ===================================================================

    def search_threads_by_keyword(
        self,
        threads: List[dict],
        keywords: List[str],
    ) -> List[dict]:
        """Lọc threads theo từ khóa (client-side filter).

        Args:
            threads: Danh sách threads.
            keywords: Danh sách từ khóa cần tìm.

        Returns:
            Danh sách threads có chứa ít nhất 1 từ khóa.
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
        title_candidate = text[:_MAX_TITLE_LENGTH]
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
    display_title = topic_title if topic_title else thread_text[:_MAX_TITLE_LENGTH]

    print_substep(
        f"Video sẽ được tạo từ trending: {display_title[:100]}...",
        style="bold green",
    )
    print_substep(f"Thread URL: {thread_url}", style="bold green")
    print_substep(f"Tác giả: @{thread_username}", style="bold blue")

    content: dict = {
        "thread_url": thread_url,
        "thread_title": display_title[:_MAX_TITLE_LENGTH],
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


def _get_google_trends_content(
    max_comment_length: int,
    min_comment_length: int,
) -> Optional[dict]:
    """Lấy nội dung từ Threads dựa trên từ khóa trending của Google Trends.

    Kết hợp Google Trends (lấy từ khóa) + Playwright (tìm bài viết trên Threads).
    Trả về None nếu không thể lấy content (để fallback sang user threads).
    """
    from threads.google_trends import (
        GoogleTrendsError,
        get_threads_from_google_trends,
    )
    from threads.trending import scrape_thread_replies

    try:
        google_threads = get_threads_from_google_trends()
    except GoogleTrendsError as e:
        print_substep(f"⚠️ Lỗi lấy Google Trends: {e}", style="bold yellow")
        return None
    except Exception as e:
        print_substep(
            f"⚠️ Lỗi không mong đợi khi lấy Google Trends: {e}",
            style="bold yellow",
        )
        return None

    if not google_threads:
        print_substep(
            "⚠️ Không tìm thấy bài viết Threads nào từ Google Trends keywords.",
            style="bold yellow",
        )
        return None

    # Chọn thread phù hợp (chưa tạo video, không chứa từ bị chặn)
    thread = None
    for t in google_threads:
        text = t.get("text", "")
        if not text or _contains_blocked_words(text):
            continue
        title_candidate = text[:_MAX_TITLE_LENGTH]
        if is_title_used(title_candidate):
            print_substep(
                f"Bỏ qua thread đã tạo video: {text[:50]}...",
                style="bold yellow",
            )
            continue
        thread = t
        break

    if thread is None:
        if google_threads:
            thread = google_threads[0]
        else:
            return None

    thread_text = thread.get("text", "")
    thread_username = thread.get("username", "unknown")
    thread_url = thread.get("permalink", "")
    shortcode = thread.get("shortcode", "")
    keyword = thread.get("keyword", "")

    # Dùng keyword làm tiêu đề video nếu có
    display_title = keyword if keyword else thread_text[:_MAX_TITLE_LENGTH]

    print_substep(
        f"Video sẽ được tạo từ Google Trends: {display_title[:100]}...",
        style="bold green",
    )
    print_substep(f"Thread URL: {thread_url}", style="bold green")
    print_substep(f"Tác giả: @{thread_username}", style="bold blue")
    print_substep(f"Từ khóa Google Trends: {keyword}", style="bold blue")

    content: dict = {
        "thread_url": thread_url,
        "thread_title": display_title,
        "thread_id": re.sub(
            r"[^\w\s-]", "",
            shortcode or f"gtrends_{hash(thread_text) % 10**8}",
        ),
        "thread_author": f"@{thread_username}",
        "is_nsfw": False,
        "thread_post": thread_text,
        "comments": [],
    }

    if not settings.config["settings"].get("storymode", False):
        # Lấy replies bằng scraping
        try:
            if thread_url:
                raw_replies = scrape_thread_replies(thread_url, limit=50)
            else:
                raw_replies = []
        except Exception as exc:
            print_substep(
                f"⚠️ Lỗi lấy replies (Google Trends): {exc}",
                style="bold yellow",
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
                        r"[^\w\s-]", "", f"gtrends_reply_{idx}"
                    ),
                    "comment_author": f"@{reply_username}",
                }
            )

    print_substep(
        f"Đã lấy nội dung từ Google Trends thành công! "
        f"({len(content.get('comments', []))} replies)",
        style="bold green",
    )
    return content


def _select_best_thread(
    client: ThreadsClient,
    threads_list: List[dict],
    min_comments: int,
) -> Optional[dict]:
    """Chọn thread tốt nhất từ danh sách, ưu tiên theo engagement.

    Tiêu chí chọn (theo thứ tự ưu tiên):
    1. Chưa tạo video (title chưa dùng)
    2. Không chứa blocked words
    3. Có đủ số replies tối thiểu (dùng has_replies field + conversation API)
    4. Engagement cao nhất (views, likes - dùng Insights API)

    Args:
        client: ThreadsClient instance.
        threads_list: Danh sách threads candidates.
        min_comments: Số replies tối thiểu yêu cầu.

    Returns:
        Thread dict tốt nhất, hoặc None nếu không tìm thấy.
    """
    # Giai đoạn 1: Lọc cơ bản (nhanh, không cần API call)
    candidates: List[dict] = []
    for t in threads_list:
        text = t.get("text", "")
        if not text or _contains_blocked_words(text):
            continue
        # Bỏ qua replies (chỉ lấy threads gốc)
        if t.get("is_reply"):
            continue
        title_candidate = text[:_MAX_TITLE_LENGTH]
        if is_title_used(title_candidate):
            print_substep(
                f"Bỏ qua thread đã tạo video: {text[:50]}...",
                style="bold yellow",
            )
            continue
        candidates.append(t)

    if not candidates:
        return None

    # Giai đoạn 2: Kiểm tra replies + lấy engagement (cần API call)
    # Dùng conversation endpoint thay vì replies để có full tree
    best_thread = None
    best_score = -1

    for t in candidates:
        thread_id = t.get("id", "")
        try:
            # Dùng conversation endpoint để lấy toàn bộ conversation tree
            # thay vì chỉ top-level replies
            conversation = client.get_conversation(
                thread_id, limit=min_comments + 10
            )
            reply_count = len(conversation)

            if reply_count < min_comments:
                continue

            # Thử lấy engagement score (optional - không fail nếu insights unavailable)
            score = reply_count  # Base score = số replies
            try:
                engagement = client.get_thread_engagement(thread_id)
                score = (
                    engagement.get("views", 0) * _SCORE_WEIGHT_VIEWS
                    + engagement.get("likes", 0) * _SCORE_WEIGHT_LIKES
                    + engagement.get("replies", 0) * _SCORE_WEIGHT_REPLIES
                    + engagement.get("reposts", 0) * _SCORE_WEIGHT_REPOSTS
                )
            except (ThreadsAPIError, requests.RequestException):
                # Insights không khả dụng → dùng reply_count làm score
                pass

            if score > best_score:
                best_score = score
                best_thread = t

        except Exception:
            continue

    return best_thread


def get_threads_posts(POST_ID: str = None) -> dict:
    """Lấy nội dung từ Threads để tạo video.

    Flow:
    1. Validate/refresh token
    2. Chọn source: trending → google_trends → user (có fallback)
    3. Chọn thread tốt nhất (dựa trên engagement nếu có)
    4. Lấy conversation tree (thay vì chỉ direct replies)
    5. Trả về content dict

    Args:
        POST_ID: ID cụ thể của thread. Nếu None, tự động chọn.

    Returns:
        Dict chứa thread content và replies.

    Raises:
        ThreadsAPIError: Nếu token không hợp lệ hoặc API trả về lỗi.
        ValueError: Nếu không tìm thấy threads phù hợp.
    """
    print_substep("Đang kết nối với Threads API...")

    client = ThreadsClient()

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
    source = thread_config.get("source", "trending")

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
        # Fallback: trending thất bại → thử Google Trends
        print_substep(
            "⚠️ Trending không khả dụng, thử lấy từ Google Trends...",
            style="bold yellow",
        )
        content = _get_google_trends_content(
            max_comment_length=max_comment_length,
            min_comment_length=min_comment_length,
        )
        if content is not None:
            return content
        print_substep(
            "⚠️ Google Trends cũng không khả dụng, chuyển sang user threads...",
            style="bold yellow",
        )

    # ------------------------------------------------------------------
    # Source: google_trends  –  Lấy bài viết dựa trên Google Trends
    # ------------------------------------------------------------------
    if source == "google_trends" and not POST_ID:
        content = _get_google_trends_content(
            max_comment_length=max_comment_length,
            min_comment_length=min_comment_length,
        )
        if content is not None:
            return content
        # Fallback: Google Trends thất bại → tiếp tục dùng user threads
        print_substep(
            "⚠️ Google Trends không khả dụng, chuyển sang lấy từ user threads...",
            style="bold yellow",
        )

    # ------------------------------------------------------------------
    # Source: user  (mặc định) hoặc POST_ID cụ thể
    # ------------------------------------------------------------------
    if POST_ID:
        # Lấy thread cụ thể theo ID (dùng full fields)
        thread = client.get_thread_by_id(POST_ID)
    else:
        # Lấy threads mới nhất và chọn thread phù hợp
        target_user = thread_config.get("target_user_id", "") or client.user_id
        threads_list = client.get_user_threads(user_id=target_user, limit=25)

        if not threads_list:
            print_substep(
                "⚠️ Không tìm thấy threads từ user API!\n"
                f"   - User ID đang dùng: {target_user}\n"
                "   Đang thử lấy bài viết từ Google Trends...",
                style="bold yellow",
            )
            # Fallback cuối cùng: thử Google Trends khi user threads cũng thất bại
            if source != "google_trends":  # Tránh gọi lại nếu đã thử
                content = _get_google_trends_content(
                    max_comment_length=max_comment_length,
                    min_comment_length=min_comment_length,
                )
                if content is not None:
                    return content
            print_substep(
                "❌ Không tìm thấy threads nào!\n"
                "   Kiểm tra các nguyên nhân sau:\n"
                f"   - User ID đang dùng: {target_user}\n"
                "   - User này có bài viết công khai không?\n"
                "   - Token có quyền threads_basic?\n"
                "   - Token có đúng cho user_id này không?\n"
                "   - Google Trends fallback cũng không tìm thấy bài viết.",
                style="bold red",
            )
            raise ValueError(
                f"No threads found for user '{target_user}'. "
                "Verify the user has public posts and the access token has "
                "'threads_basic' permission."
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

        # Chọn thread tốt nhất (dựa trên engagement + conversation)
        thread = _select_best_thread(
            client, threads_list, min_comments=min_comments
        )

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

    # Hiển thị engagement nếu có
    try:
        engagement = client.get_thread_engagement(thread_id)
        if engagement:
            stats = ", ".join(
                f"{k}: {v}" for k, v in engagement.items() if v
            )
            if stats:
                print_substep(f"📊 Engagement: {stats}", style="bold blue")
    except (ThreadsAPIError, requests.RequestException):
        pass  # Insights không khả dụng → bỏ qua

    content: dict = {
        "thread_url": thread_url,
        "thread_title": thread_text[:_MAX_TITLE_LENGTH],
        "thread_id": re.sub(r"[^\w\s-]", "", thread_id),
        "thread_author": f"@{thread_username}",
        "is_nsfw": False,
        "thread_post": thread_text,
        "comments": [],
    }

    if settings.config["settings"].get("storymode", False):
        # Story mode - đọc toàn bộ nội dung bài viết
        content["thread_post"] = thread_text
    else:
        # Comment mode - dùng conversation endpoint để lấy full tree
        # thay vì chỉ direct replies (conversation bao gồm cả nested replies)
        try:
            conversation = client.get_conversation(thread_id, limit=100)
        except (ThreadsAPIError, requests.RequestException):
            # Fallback sang direct replies nếu conversation không khả dụng
            try:
                conversation = client.get_thread_replies(thread_id, limit=50)
            except Exception as e:
                print_substep(f"Lỗi khi lấy replies: {e}", style="bold red")
                conversation = []

        for reply in conversation:
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
